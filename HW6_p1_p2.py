import numpy as np
import scr.StatisticalClasses as Stat


class Game(object):
    def __init__(self, id, prob_head):
        self._id = id
        self._rnd = np.random
        self._rnd.seed(id)
        self._probHead = prob_head  # probability of flipping a head
        self._countWins = 0  # number of wins, set to 0 to begin

    def simulate(self, n_of_flips):

        count_tails = 0  # number of consecutive tails so far, set to 0 to begin

        # flip the coin 20 times
        for i in range(n_of_flips):

            # in the case of flipping a heads
            if self._rnd.random_sample() < self._probHead:
                if count_tails >= 2:  # if the series is ..., T, T, H
                    self._countWins += 1  # increase the number of wins by 1
                count_tails = 0  # the tails counter needs to be reset to 0 because a heads was flipped

            # in the case of flipping a tails
            else:
                count_tails += 1  # increase tails count by one

    def get_reward(self):
        # calculate the reward from playing a single game
        return 100*self._countWins - 250


class SetOfGames:
    def __init__(self, prob_head, n_games):
        self._games = []
        self._gameRewards = [] # create an empty list where rewards will be stored
        self._initialGameSize = n_games  # initial game size
        self._loss= []
        # populate the repeatation
        for n in range(n_games):
            game = Game(id=n, prob_head=prob_head)
            self._games.append(game)

        # simulate the games
    def simulate(self, n_of_flips):
        for game in self._games:
            game.simulate(n_of_flips)
            self._gameRewards.append(game.get_reward())

        return GameOutcomes(self)

    def get_ave_reward(self):
        """ returns the average reward from all games"""
        return sum(self._gameRewards) / len(self._gameRewards)

    def get_reward_list(self):
        """ returns all the rewards from all game to later be used for creation of histogram """
        return self._gameRewards

    def get_probability_loss(self):
        """ returns the probability of a loss """
        return sum(self._loss)/len(self._loss)

    def get_loss_time(self):
        for value in self._gameRewards:
            if value < 0:
                self._loss.append(1)
            else:
                self._loss.append(0)
        return self._loss

    def get_initial_game_size(self):
        """ :returns the initial population size of this cohort"""
        return self._initialGameSize


class GameOutcomes:

    def __init__(self, simulated_game):
        self._simulatedGame= simulated_game

    # summary statistics on expected reward
        self._sumStat_Reward = \
            Stat.SummaryStat('The Rewards list', self._simulatedGame.get_reward_list())
        self._sumStat_Lossprob=\
            Stat.SummaryStat("Loss Probability", self._simulatedGame.get_loss_time())

    def get_ave_reward(self):
        """ returns the average reward from all games"""
        return self._sumStat_Reward.get_mean()

    def get_CI_expected_reward(self, alpha):
        """
        :param alpha: confidence level
        :return: t-based confidence interval
        """
        return self._sumStat_Reward.get_t_CI(alpha)

    def get_CI_loss_probability(self,alpha):
        return self._sumStat_Lossprob.get_t_CI(alpha)


# Calculate expected reward of 1000 games
trial = SetOfGames(prob_head=0.5, n_games=1000)
gameOutcome=trial.simulate(20)
ALPHA=0.05

# check the list of rewards and loss game
print(trial.get_reward_list())
print(trial.get_loss_time())

# Problem 1: Print the average expected reward and its 95% CI
print("The average expected rewards is:", trial.get_ave_reward())
print('95% CI of average expected rewards (dollars)', gameOutcome.get_CI_expected_reward(ALPHA))

# Find the probability of a loss and its 95% CI
print("The probability of a single game yielding a loss is:", trial.get_probability_loss())
print('95% CI of loss probability', gameOutcome.get_CI_loss_probability(ALPHA))

# Problem 2: Interpretation of Confidence Interval
# For expected rewards: When we repeat the game 1000 times
# there are 95% of the CI we get will cover the true expected rewards
# For loss probability: When we repeat the game 1000 times
# there are 95% of the CI we get will cover the true loss probability

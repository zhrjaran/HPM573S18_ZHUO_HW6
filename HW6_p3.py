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
    def __init__(self,id, prob_head, n_games):
        """
        :param id: setofGames id
        :param prob_head: the probability of head
        :param n_games: the number of games in this set
        """
        self._games = []
        self._gameRewards = [] # create an empty list where rewards will be stored
        self._initialGameSize = n_games  # initial game size
        self._loss= []
        # populate the repeatation
        for n in range(n_games):
            game = Game(id=id*n_games+n, prob_head=prob_head)
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

class MultiGame:
    """simulate multiple games with different parameters"""
    def __init__(self,ids, gambler_n_games, prob_heads):
        """
        :param ids: a list of ids for games to simulate
        :param gambler_n_games:  a list of game sizes of each game to simulate
        :param prob_heads: a list of the "head" probabilities
        """
        self._id= ids
        self._gamblergamesize= gambler_n_games
        self._headprob= prob_heads

        self._gameRewards = []  # two dimensional list where rewards will be stored
        self._meangameRewards= [] # list of expected/mean rewards for each game will get

    def simulate(self, n_of_flips):
        for i in range(len(self._id)):
            # create a setofGame
            game=SetOfGames(id=self._id[i], prob_head=self._headprob[i], n_games=self._gamblergamesize[i])
            # simulate this setofGame
            output=game.simulate(n_of_flips)
            # store each flip's rewards
            self._gameRewards.append(game.get_reward_list())
            # get the mean/expected rewards of each setofGame
            self._meangameRewards.append(output.get_ave_reward())

        # after simulating all setofGames
        # summary statistics of mean game rewards
        self._sumStat_meangameRewards = Stat.SummaryStat('Mean Game Rewards', self._meangameRewards)
    def get_all_expectedRewards(self):
        """
        :return: a list of expected/mean rewards for all simulated setofGames
        """
        return self._meangameRewards

    def get_overall_expectedRewards(self):
        """
        :return: overall expected/mean rewards across all simulated setofGames
        """
        return self._sumStat_meangameRewards.get_mean()

    def get_PI_expected_rewards(self, alpha):
        """ :returns: the prediction interval of the expected rewards"""
        return self._sumStat_meangameRewards.get_PI(alpha)


HEAD_PROB = 0.5    # annual probability of mortality
NUM_FLIPS = 20        # simulation length
EACH_GAMBLER_SIZE = 10     # size of the real games to make the projections for gambler
EACH_CASINO_SIZE= 1000   # size of the real games to make the projections for casino owner
NUM_SIM_GAMES = 1000   # number of simulated games used for making projections
ALPHA = 0.05     # significance level

# For Casino owner, since he/she played the game many times, thus obey the large number rules
# Print the average expected rewards and its 95% CI
trial = SetOfGames(id=2, prob_head=HEAD_PROB, n_games=EACH_CASINO_SIZE)
gameOutcome=trial.simulate(NUM_FLIPS)


# Print the average expected reward and its 95% CI
print("The average expected rewards for casino owner is:", trial.get_ave_reward())
print('95% CI of average expected rewards for casino owner (dollars):', gameOutcome.get_CI_expected_reward(ALPHA))
print('The interpretation of 95% CI: For casino owner, he/she plays games for 1000 times,',
      'there are 95% of CI we get will contain the true expected rewards')

# For gambler, since he/she only play game 10 times, this is a small sample size
# Thus, we should print the 95% PI for gambler

# Calculate expected reward of 1000 games
multitrial = MultiGame(
    ids= range(NUM_SIM_GAMES),
    gambler_n_games=[EACH_GAMBLER_SIZE]* NUM_SIM_GAMES,
    prob_heads=[HEAD_PROB]* NUM_SIM_GAMES)


# simulate all setofGames
gameOutcome=multitrial.simulate(NUM_FLIPS)
# print projected mean survival time (years)
print('Projected average expected rewards for gambler is:',
      multitrial.get_overall_expectedRewards())

# print projection interval of average expected rewards
print('95% PI of average expected rewards for gambler (dollars):',
      multitrial.get_PI_expected_rewards(ALPHA))
print('The interpretation of 95% PI: For gambler,',
      'we have 95% probability that next observation will fall in this range of PI')






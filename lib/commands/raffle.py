import lib.twitch as twitch
import random
import time

#Command !raffle, !cancelraffle, !makeraffle, !pickwinner

class Raffle():
    """Class representing and handling a raffle."""

    def __init__(self):
        self._lastWinner = None
        self._active = False
        self._prize = ""
        self._entered = []
        self._startTime = None
        self._winner = None

    def start_raffle(self, userName, *args, **kwargs):
        """Start a raffle if one is not active."""
        if self._active:
            return ["There is already a raffle in progress. !cancelraffle or !pickwinner first!"]
        else:
            self._active = True
            self._prize = ' '.join(args)
            self._entered = []
            self._startTime = time.time()
            self._winner = None
            return ["A raffle for {} has been initiated! Join it by using !raffle :D".format(self._prize)]

    def enter_user(self, userName, *args, **kwargs):
        """Enter a user into the entrants list if a raffle is active."""
        if self._active:
            if userName not in self._entered:
                if twitch.is_follower(userName):
                    self._entered.append(userName)
                    return ["/w {} You have been entered in the raffle for {}!".format(userName, self._prize)]
                else:
                    return ["/w {} Sorry, raffles are only available to followers! Give the channel a follow and try again! :)".format(userName)]
        return None

    def cancel_raffle(self, userName, *args, **kwargs):
        """Cancel a raffle if one is active."""        
        if self._active:
            self._active = False
            return ["Raffle cancelled"]
        else:
            return ["No active raffle! Start one with !makeraffle"]

    def choose_winner(self, userName, *args, **kwargs):
        """Chose a winner from the list of entrants."""
        if self._active:
            if len(self._entered) == 0:
                return self.cancel_raffle(userName, args)
            self._winner = self._entered[random.randint(0, len(self._entered)-1)]
            self._lastWinner = self._winner
            self._active = False
            return ["{} has won {}! Contact a moderator to receive your prize! :)".format(self._winner, self._prize)]
        else:
            return None
    
raffle = Raffle()
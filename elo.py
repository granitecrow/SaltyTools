import math

K = 30

def Probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


def DetermineNewRankings(winnerRa, winnerPa, loserRb, loserPb):
    winnerRa = winnerRa + K * (1 - winnerPa) 
    loserRb = loserRb + K * (0 - loserPb)
    return (winnerRa, loserRb)
    
def ExpectedProbabilities(Ra, Rb):
    #Probability of Player A
    Pa = Probability(Rb, Ra)
    #Probability of Player B
    Pb = Probability(Ra, Rb)
    return (Pa, Pb)
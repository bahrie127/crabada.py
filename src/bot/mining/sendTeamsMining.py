"""
Send a user's available teams mining
"""

from src.common.logger import logger
from src.common.txLogger import txLogger, logTx
from src.helpers.instantMessage import sendIM
from src.common.clients import makeCrabadaWeb3Client
from src.helpers.teams import fetchAvailableTeamsForTask
from src.models.User import User
from web3.exceptions import *
from src.common.dotenv import getenv


def sendTeamsMining(user: User) -> int:
    """
    Send mining the available teams with the 'mine' task.

    Returns the opened mines
    """
    client = makeCrabadaWeb3Client(
        upperLimitForBaseFeeInGwei=user.config["mineMaxGasInGwei"])
    availableTeams = fetchAvailableTeamsForTask(user, "mine")

    if not availableTeams:
        logger.info("No available teams to send mining for user " + str(user.address))
        return 0

    # Send the teams
    nSentTeams = 0
    for t in availableTeams:

        # Send team
        teamId = t["team_id"]
        logger.info(f"Sending team {teamId} to mine...")
        try:
            txHash = client.startGame(teamId)
        except ContractLogicError as e:
            logger.warning(f"Error sending team {teamId} mining: {e}")
            sendIM(getenv("BOT_ID") + f" , Error sending team {teamId} mining: {e}")
            continue
        except SolidityError as sol:
            logger.warning(f"Error sending team {teamId} mining: SolidityError {sol}")
            sendIM(getenv("BOT_ID") + f" , Error sending team {teamId} mining: SolidityError {sol}")
            continue

        # Report
        txLogger.info(txHash)
        txReceipt = client.getTransactionReceipt(txHash)
        logTx(txReceipt)
        if txReceipt["status"] != 1:
            logger.error(f"Error sending team {teamId} mining")
            sendIM(getenv("BOT_ID") + f" , Error sending team {teamId} mining")
        else:
            nSentTeams += 1
            logger.info(f"Team {teamId} sent successfully")
            sendIM(getenv("BOT_ID") + f" , Team {teamId} sent successfully")

    return nSentTeams

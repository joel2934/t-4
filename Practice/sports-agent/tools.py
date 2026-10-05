import os
import requests

from dotenv import load_dotenv
from langchain_core.tools import tool


load_dotenv()


@tool
def get_cricket_scores() -> str:
    """
    Get current cricket matches and their live scores.

    Use this tool when the user asks about:
    - current cricket matches
    - live cricket scores
    - teams currently playing
    - ongoing cricket matches
    """

    api_key = os.getenv("CRICKET_API_KEY")

    if not api_key:
        return (
            "Cricket API key is not configured. "
            "Please add CRICKET_API_KEY to the .env file."
        )

    url = "https://api.cricapi.com/v1/currentMatches"

    params = {
        "apikey": api_key,
        "offset": 0
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        result = response.json()

    except requests.RequestException as e:

        return f"Cricket API request failed: {e}"

    except ValueError:

        return (
            "Cricket API returned an invalid JSON response."
        )


    # Check API response status if available
    if result.get("status") == "failure":

        return (
            "Cricket API returned an error: "
            + str(result)
        )


    matches = result.get("data", [])


    if not matches:

        return (
            "There are currently no cricket matches "
            "available from the API."
        )


    formatted_matches = []


    for match in matches:

        name = match.get(
            "name",
            "Unknown match"
        )

        status = match.get(
            "status",
            "Unknown status"
        )

        venue = match.get(
            "venue",
            "Unknown venue"
        )

        teams = match.get(
            "teams",
            []
        )

        score_data = match.get(
            "score",
            []
        )


        # -----------------------------
        # Format teams
        # -----------------------------

        if teams:

            teams_text = " vs ".join(
                str(team)
                for team in teams
            )

        else:

            teams_text = "Teams unavailable"


        # -----------------------------
        # Format scores
        # -----------------------------

        if score_data:

            innings_scores = []


            for score in score_data:

                runs = score.get(
                    "r",
                    "?"
                )

                wickets = score.get(
                    "w",
                    "?"
                )

                overs = score.get(
                    "o",
                    "?"
                )

                innings_scores.append(
                    f"{runs}/{wickets} "
                    f"({overs} overs)"
                )


            score_text = " | ".join(
                innings_scores
            )

        else:

            score_text = (
                "Score not available"
            )


        # -----------------------------
        # Format match
        # -----------------------------

        formatted_match = (
            f"Match: {name}\n"
            f"Status: {status}\n"
            f"Teams: {teams_text}\n"
            f"Venue: {venue}\n"
            f"Score: {score_text}"
        )


        formatted_matches.append(
            formatted_match
        )


    return "\n\n".join(
        formatted_matches
    )
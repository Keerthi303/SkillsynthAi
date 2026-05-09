"""
LeetCode Service — Analyze LeetCode profiles via GraphQL API.
"""
import logging
import requests

logger = logging.getLogger(__name__)

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

PROFILE_QUERY = """
query userProfile($username: String!) {
    matchedUser(username: $username) {
        username
        profile {
            realName
            ranking
            reputation
            starRating
        }
        submitStatsGlobal {
            acSubmissionNum {
                difficulty
                count
            }
        }
        tagProblemCounts {
            advanced { tagName tagSlug problemsSolved }
            intermediate { tagName tagSlug problemsSolved }
            fundamental { tagName tagSlug problemsSolved }
        }
    }
    userContestRanking(username: $username) {
        attendedContestsCount
        rating
        globalRanking
        topPercentage
    }
}
"""


def fetch_leetcode_profile(username: str) -> dict:
    """Fetch LeetCode profile data via GraphQL."""
    try:
        resp = requests.post(
            LEETCODE_GRAPHQL,
            json={"query": PROFILE_QUERY, "variables": {"username": username}},
            headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})

        user = data.get("matchedUser")
        if not user:
            return {"error": f"LeetCode user '{username}' not found"}

        # Parse submission stats
        stats = user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
        solved = {"All": 0, "Easy": 0, "Medium": 0, "Hard": 0}
        for s in stats:
            solved[s["difficulty"]] = s["count"]

        # Parse topic stats
        topics = {}
        for level in ["fundamental", "intermediate", "advanced"]:
            for tag in user.get("tagProblemCounts", {}).get(level, []):
                topics[tag["tagName"]] = {"solved": tag["problemsSolved"], "level": level}

        # Contest data
        contest = data.get("userContestRanking") or {}

        return {
            "username": user.get("username"),
            "real_name": user.get("profile", {}).get("realName"),
            "ranking": user.get("profile", {}).get("ranking"),
            "total_solved": solved["All"],
            "easy_solved": solved["Easy"],
            "medium_solved": solved["Medium"],
            "hard_solved": solved["Hard"],
            "contest_rating": round(contest.get("rating", 0)) if contest.get("rating") else None,
            "contests_attended": contest.get("attendedContestsCount", 0),
            "global_ranking": contest.get("globalRanking"),
            "top_percentage": contest.get("topPercentage"),
            "topics": topics,
        }
    except requests.RequestException as e:
        logger.error("LeetCode API error: %s", e)
        return {"error": f"Failed to fetch LeetCode data: {str(e)}"}


def analyze_leetcode(username: str) -> dict:
    """Analyze LeetCode profile and return structured data."""
    profile = fetch_leetcode_profile(username)
    if "error" in profile:
        return profile

    total = profile["total_solved"]
    easy = profile["easy_solved"]
    medium = profile["medium_solved"]
    hard = profile["hard_solved"]

    # Determine DSA readiness level
    if total >= 500 or (hard >= 50 and medium >= 150):
        dsa_level = "Advanced"
        dsa_score = min(95, 70 + hard + medium // 5)
    elif total >= 150 or (medium >= 50 and hard >= 10):
        dsa_level = "Intermediate"
        dsa_score = min(70, 30 + total // 5 + hard * 2)
    else:
        dsa_level = "Beginner"
        dsa_score = min(30, total // 3)

    # Identify strong and weak topics
    strong_topics = []
    weak_topics = []
    for topic, data in profile.get("topics", {}).items():
        if data["solved"] >= 10:
            strong_topics.append(topic)
        elif data["solved"] <= 3 and data["level"] in ["fundamental", "intermediate"]:
            weak_topics.append(topic)

    return {
        **profile,
        "dsa_readiness_level": dsa_level,
        "dsa_readiness_score": dsa_score,
        "strong_topics": strong_topics[:10],
        "weak_topics": weak_topics[:10],
    }

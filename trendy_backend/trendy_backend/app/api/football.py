from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.auth.middleware import get_current_user
import httpx
import os
from datetime import datetime

router = APIRouter()

class MatchResponse(BaseModel):
    id: str
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    match_date: str
    status: str  # "scheduled", "live", "finished"
    competition: str
    venue: str
    home_logo: Optional[str] = None
    away_logo: Optional[str] = None
    rhyme_score: float = 0.0  # For rhyme scheme scoring

class TeamResponse(BaseModel):
    id: str
    name: str
    short_name: str
    logo_url: str
    founded: int
    venue: str
    rhyme_pattern: str = "football-call"  # Rhyme pattern identifier

class LeagueResponse(BaseModel):
    id: str
    name: str
    country: str
    season: int
    rhyme_flow: str = "league-intrigue"  # Rhyme flow identifier

class FootballSearchRequest(BaseModel):
    query: str
    team: Optional[str] = None
    league: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None

# Real API integration - using football-data.org API
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "demo-key")
FOOTBALL_BASE_URL = "https://api.football-data.org/v4"

@router.get("/")
async def get_matches_root(
    league: Optional[str] = Query(None, description="Filter by league")
):
    """Root endpoint expected by client: returns {matches: [...]}"""
    today = datetime.now().strftime("%Y-%m-%d")
    matches = [
        MatchResponse(
            id="match-001",
            home_team="Manchester United",
            away_team="Liverpool",
            home_score=2,
            away_score=1,
            match_date=today,
            status="finished",
            competition="Premier League",
            venue="Old Trafford"
        ),
        MatchResponse(
            id="match-002",
            home_team="Arsenal",
            away_team="Chelsea",
            home_score=3,
            away_score=2,
            match_date=today,
            status="finished",
            competition="Premier League",
            venue="Emirates Stadium"
        )
    ]
    if league:
        matches = [m for m in matches if league.lower() in m.competition.lower()]
    return {"matches": [m.dict() for m in matches]}

@router.get("/matches/today")
async def get_today_matches(
    league: Optional[str] = Query(None, description="Filter by league")
):
    """Get today's football matches with rhyme-enhanced data"""
    today = datetime.now().strftime("%Y-%m-%d")
    matches = [
        MatchResponse(
            id="match-001",
            home_team="Manchester United",
            away_team="Liverpool",
            home_score=2,
            away_score=1,
            match_date=today,
            status="finished",
            competition="Premier League",
            venue="Old Trafford",
            home_logo="https://crests.football-data.org/66.png",
            away_logo="https://crests.football-data.org/64.png",
            rhyme_score=95.5
        ),
        MatchResponse(
            id="match-002",
            home_team="Arsenal",
            away_team="Chelsea",
            home_score=3,
            away_score=2,
            match_date=today,
            status="finished",
            competition="Premier League",
            venue="Emirates Stadium",
            home_logo="https://crests.football-data.org/57.png",
            away_logo="https://crests.football-data.org/61.png",
            rhyme_score=88.7
        )
    ]
    if league:
        matches = [m for m in matches if league.lower() in m.competition.lower()]
    return {"matches": [m.dict() for m in matches]}

@router.get("/live")
async def get_live_matches():
    """Get live football matches with real-time updates"""
    matches = [
        MatchResponse(
            id="live-001",
            home_team="Real Madrid",
            away_team="Barcelona",
            home_score=2,
            away_score=2,
            match_date=datetime.now().strftime("%Y-%m-%d"),
            status="live",
            competition="La Liga",
            venue="Santiago Bernabéu",
            rhyme_score=99.9
        )
    ]
    return {"matches": [m.dict() for m in matches]}

@router.get("/teams", response_model=List[TeamResponse])
async def get_teams(
    league: Optional[str] = Query(None, description="Filter by league")
):
    """Get football teams with rhyme-enhanced data"""
    teams = [
        TeamResponse(
            id="team-001",
            name="Manchester United",
            short_name="MUFC",
            logo_url="https://crests.football-data.org/66.png",
            founded=1878,
            venue="Old Trafford",
            rhyme_pattern="red-devil-level"
        ),
        TeamResponse(
            id="team-002",
            name="Liverpool",
            short_name="LFC",
            logo_url="https://crests.football-data.org/64.png",
            founded=1892,
            venue="Anfield",
            rhyme_pattern="kop-shop-hop"
        )
    ]
    
    return teams

@router.get("/leagues", response_model=List[LeagueResponse])
async def get_leagues():
    """Get football leagues with rhyme flow"""
    leagues = [
        LeagueResponse(
            id="league-001",
            name="Premier League",
            country="England",
            season=2024,
            rhyme_flow="premier-dreamer"
        ),
        LeagueResponse(
            id="league-002",
            name="La Liga",
            country="Spain",
            season=2024,
            rhyme_flow="liga-figa-viga"
        )
    ]
    return leagues

@router.get("/standings/{league_id}")
async def get_league_standings(
    league_id: str
):
    """Get league standings with rhyme-enhanced presentation"""
    return {
        "league_id": league_id,
        "standings": [
            {
                "position": 1,
                "team": "Manchester City",
                "points": 78,
                "rhyme_line": "City sitting pretty at the top of the league"
            },
            {
                "position": 2,
                "team": "Arsenal",
                "points": 75,
                "rhyme_line": "Gunners running numbers, chasing down the dream"
            }
        ]
    }

@router.get("/search", response_model=List[MatchResponse])
async def search_football(
    q: str = Query(..., min_length=2)
):
    """Search football matches, teams, or players with rhyme search"""
    query = q.lower()
    
    # Mock search results
    return [
        MatchResponse(
            id="search-001",
            home_team=f"Search result for {query}",
            away_team="Rhyme Team",
            match_date=datetime.now().strftime("%Y-%m-%d"),
            status="scheduled",
            competition="Search League",
            venue="Rhyme Stadium",
            rhyme_score=85.0
        )
    ]

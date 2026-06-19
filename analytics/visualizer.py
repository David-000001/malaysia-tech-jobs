import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from datetime import datetime

# Coordinated mapping for Malaysian tech hubs
HUB_COORDINATES = {
    "bangsar south": (3.1116, 101.6654, "Bangsar South (KL)"),
    "kl sentral": (3.1344, 101.6861, "KL Sentral (KL)"),
    "cyberjaya": (2.9213, 101.6514, "Cyberjaya (Selangor)"),
    "mid valley": (3.1186, 101.6781, "Mid Valley (KL)"),
    "petaling jaya": (3.1578, 101.6116, "Petaling Jaya (Selangor)"),
    "mutiara damansara": (3.1578, 101.6116, "Petaling Jaya (Selangor)"),
    "shah alam": (3.0738, 101.5183, "Shah Alam (Selangor)"),
    "subang jaya": (3.0801, 101.5822, "Subang Jaya (Selangor)"),
    "puchong": (3.0236, 101.6189, "Puchong (Selangor)"),
    "klcc": (3.1582, 101.7140, "KLCC (KL)"),
    "kuala lumpur": (3.1390, 101.6869, "Kuala Lumpur"),
    "selangor": (3.0738, 101.5183, "Selangor")
}

def get_coordinates_for_location(loc_text):
    """Maps a location text to latitude, longitude and a formatted hub name."""
    if not loc_text:
        return 3.1390, 101.6869, "Kuala Lumpur" # Default to KL Center
        
    loc_lower = loc_text.lower()
    
    for key, (lat, lon, name) in HUB_COORDINATES.items():
        if key in loc_lower:
            return lat, lon, name
            
    # Default fallback to center of KL/Selangor area
    if "selangor" in loc_lower:
        return 3.0738, 101.5183, "Selangor"
    return 3.1390, 101.6869, "Kuala Lumpur"

def generate_skill_demand_chart(jobs):
    """Generates a horizontal bar chart of the Top 10 most demanded tech skills."""
    if not jobs:
        # Return empty figure
        return px.bar(title="No job data available")
        
    # Count skills
    all_skills = []
    for job in jobs:
        skills = job.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]
        all_skills.extend(skills)
        
    skill_counts = Counter(all_skills)
    df = pd.DataFrame(skill_counts.most_common(10), columns=["Skill", "Job Postings"])
    
    # Sort in ascending order so that largest is at the top of the horizontal bar chart
    df = df.sort_values(by="Job Postings", ascending=True)
    
    fig = px.bar(
        df,
        x="Job Postings",
        y="Skill",
        orientation="h",
        title="Top 10 Most In-Demand Tech Skills (Last 30 Days)",
        color="Job Postings",
        color_continuous_scale="Tealgrn" # Dark theme friendly teal scale
    )
    
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor="#2a303d"),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=False
    )
    return fig

def generate_hiring_activity_table(jobs):
    """Aggregates active postings and lists hiring counts per company."""
    if not jobs:
        return pd.DataFrame(columns=["Company", "Active Postings", "Primary Location"])
        
    df_raw = pd.DataFrame(jobs)
    
    # Calculate totals
    summary = df_raw.groupby("company").agg(
        active_postings=("id", "count"),
        primary_location=("location", lambda x: x.mode()[0] if not x.empty else "Malaysia")
    ).reset_index()
    
    # Sort by active postings descending
    summary = summary.sort_values(by="active_postings", ascending=False)
    summary.rename(columns={"company": "Company", "active_postings": "Active Postings", "primary_location": "Primary Location"}, inplace=True)
    return summary

def generate_hiring_trends_chart(jobs):
    """Generates a time-series line chart of monthly job postings."""
    if not jobs:
        return px.line(title="No job data available")
        
    df = pd.DataFrame(jobs)
    
    # Format posting dates to Month-Year
    df["post_date"] = pd.to_datetime(df["posting_date"], errors="coerce")
    df = df.dropna(subset=["post_date"])
    df["Month"] = df["post_date"].dt.to_period("M").astype(str)
    
    # Group by Month
    trends = df.groupby("Month").size().reset_index(name="Postings")
    trends = trends.sort_values("Month")
    
    fig = px.line(
        trends,
        x="Month",
        y="Postings",
        title="Job Postings Trend Line",
        markers=True,
        line_shape="linear"
    )
    
    # Accent color styling matching teal theme
    fig.update_traces(line_color="#10b981", marker=dict(size=8, color="#059669"))
    
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor="#2a303d"),
        yaxis=dict(showgrid=True, gridcolor="#2a303d")
    )
    return fig

def generate_company_trends_chart(jobs):
    """Generates trend lines of monthly postings grouped by Top 5 companies."""
    if not jobs:
        return px.line(title="No job data available")
        
    df = pd.DataFrame(jobs)
    df["post_date"] = pd.to_datetime(df["posting_date"], errors="coerce")
    df = df.dropna(subset=["post_date"])
    df["Month"] = df["post_date"].dt.to_period("M").astype(str)
    
    # Find top 5 companies
    top_companies = df["company"].value_counts().head(5).index.tolist()
    df_filtered = df[df["company"].isin(top_companies)]
    
    # Group by Month and Company
    company_trends = df_filtered.groupby(["Month", "company"]).size().reset_index(name="Postings")
    company_trends = company_trends.sort_values("Month")
    
    fig = px.line(
        company_trends,
        x="Month",
        y="Postings",
        color="company",
        title="Hiring Activity Trends for Top 5 Companies",
        markers=True
    )
    
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor="#2a303d"),
        yaxis=dict(showgrid=True, gridcolor="#2a303d"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def generate_talent_heatmap(jobs):
    """Generates an interactive scatter map of job concentration in KL/Selangor."""
    if not jobs:
        return px.scatter_mapbox(title="No job data available")
        
    map_data = []
    for job in jobs:
        lat, lon, hub = get_coordinates_for_location(job.get("location"))
        map_data.append({
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "hub": hub,
            "lat": lat,
            "lon": lon
        })
        
    df = pd.DataFrame(map_data)
    
    # Group by lat/lon to get counts
    density = df.groupby(["lat", "lon", "hub"]).size().reset_index(name="Postings Count")
    
    fig = px.scatter_mapbox(
        density,
        lat="lat",
        lon="lon",
        size="Postings Count",
        color="Postings Count",
        hover_name="hub",
        hover_data={"lat": False, "lon": False, "Postings Count": True},
        color_continuous_scale="Tealgrn",
        zoom=10,
        center={"lat": 3.08, "lon": 101.65}, # Center in KL/Selangor tech-belt
        title="Talent Hotspot Density Map (Kuala Lumpur & Selangor)"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        template="plotly_dark",
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_showscale=True,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

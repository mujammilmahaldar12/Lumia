#!/usr/bin/env python3
"""
Lumia Robo-Advisor - Alternative Gantt Chart Generator
Creates a text-based and simplified visual Gantt chart
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def create_simple_gantt_chart():
    """
    Create a simplified Gantt chart that works in any environment
    """
    
    # Project data
    tasks = [
        {"task": "Project Planning", "start": "2024-08-01", "end": "2024-08-15", "phase": "Planning"},
        {"task": "Requirements Analysis", "start": "2024-08-10", "end": "2024-08-25", "phase": "Planning"},
        {"task": "Technology Research", "start": "2024-08-20", "end": "2024-09-05", "phase": "Planning"},
        {"task": "System Design", "start": "2024-08-25", "end": "2024-09-15", "phase": "Planning"},
        {"task": "Database Schema Design", "start": "2024-09-01", "end": "2024-09-10", "phase": "Backend"},
        {"task": "Database Models Implementation", "start": "2024-09-10", "end": "2024-09-20", "phase": "Backend"},
        {"task": "Data Collectors Development", "start": "2024-09-15", "end": "2024-10-05", "phase": "Backend"},
        {"task": "Financial Algorithms Implementation", "start": "2024-09-20", "end": "2024-10-10", "phase": "Backend"},
        {"task": "Portfolio Optimization Module", "start": "2024-09-25", "end": "2024-10-08", "phase": "Backend"},
        {"task": "API Server Development", "start": "2024-10-01", "end": "2024-10-15", "phase": "Backend"},
        {"task": "React Project Setup", "start": "2024-10-05", "end": "2024-10-08", "phase": "Frontend"},
        {"task": "UI Component Library Integration", "start": "2024-10-08", "end": "2024-10-12", "phase": "Frontend"},
        {"task": "Authentication System", "start": "2024-10-10", "end": "2024-10-18", "phase": "Frontend"},
        {"task": "Dashboard Development", "start": "2024-10-15", "end": "2024-10-25", "phase": "Frontend"},
        {"task": "Portfolio Generation Interface", "start": "2024-10-18", "end": "2024-10-28", "phase": "Frontend"},
        {"task": "Performance Charts & Analytics", "start": "2024-10-22", "end": "2024-11-02", "phase": "Frontend"},
        {"task": "Notification System", "start": "2024-10-25", "end": "2024-11-05", "phase": "Frontend"},
        {"task": "Frontend-Backend Integration", "start": "2024-10-28", "end": "2024-11-08", "phase": "Testing"},
        {"task": "Unit Testing", "start": "2024-11-01", "end": "2024-11-12", "phase": "Testing"},
        {"task": "Integration Testing", "start": "2024-11-05", "end": "2024-11-15", "phase": "Testing"},
        {"task": "Performance Testing", "start": "2024-11-08", "end": "2024-11-18", "phase": "Testing"},
        {"task": "Security Testing", "start": "2024-11-10", "end": "2024-11-20", "phase": "Testing"},
        {"task": "Database Migration Scripts", "start": "2024-11-12", "end": "2024-11-18", "phase": "Deployment"},
        {"task": "Production Environment Setup", "start": "2024-11-15", "end": "2024-11-22", "phase": "Deployment"},
        {"task": "User Documentation", "start": "2024-11-18", "end": "2024-11-28", "phase": "Deployment"},
        {"task": "Technical Documentation", "start": "2024-11-20", "end": "2024-11-30", "phase": "Deployment"},
        {"task": "Project Report Writing", "start": "2024-11-25", "end": "2024-12-10", "phase": "Deployment"},
        {"task": "Final Testing & Bug Fixes", "start": "2024-11-28", "end": "2024-12-05", "phase": "Deployment"},
        {"task": "Project Presentation Preparation", "start": "2024-12-01", "end": "2024-12-08", "phase": "Deployment"},
        {"task": "Project Submission", "start": "2024-12-08", "end": "2024-12-10", "phase": "Deployment"},
    ]
    
    # Convert to DataFrame
    df = pd.DataFrame(tasks)
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    df['duration'] = (df['end'] - df['start']).dt.days
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Phase colors
    phase_colors = {
        'Planning': '#87CEEB',
        'Backend': '#FFB6C1', 
        'Frontend': '#90EE90',
        'Testing': '#DDA0DD',
        'Deployment': '#F0E68C'
    }
    
    # Plot bars
    for i, task in df.iterrows():
        color = phase_colors.get(task['phase'], '#CCCCCC')
        ax.barh(i, task['duration'], 
               left=mdates.date2num(task['start']), 
               height=0.5, color=color, alpha=0.7, 
               edgecolor='black', linewidth=0.5)
    
    # Customize chart
    ax.set_ylim(-0.5, len(df))
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([f"{task[:30]}..." if len(task) > 30 else task 
                       for task in df['task']], fontsize=8)
    ax.invert_yaxis()
    
    # Format dates
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Title and labels
    plt.title('Lumia Robo-Advisor - Project Gantt Chart', fontsize=14, fontweight='bold')
    plt.xlabel('Timeline (2024)', fontsize=10)
    plt.ylabel('Tasks', fontsize=10)
    
    # Legend
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.7, label=phase) 
                      for phase, color in phase_colors.items()]
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Adjust layout
    plt.subplots_adjust(left=0.3, right=0.95, top=0.92, bottom=0.15)
    
    # Save chart
    plt.savefig('lumia_simple_gantt.png', dpi=200, bbox_inches='tight')
    plt.savefig('lumia_simple_gantt.pdf', bbox_inches='tight')
    
    print("✅ Simple Gantt chart saved as lumia_simple_gantt.png and .pdf")
    
    return fig

def print_text_gantt():
    """
    Create a text-based Gantt chart for terminals
    """
    print("\n" + "="*80)
    print("LUMIA ROBO-ADVISOR - PROJECT TIMELINE (TEXT FORMAT)")
    print("="*80)
    
    tasks = [
        ("Planning Phase", "Aug 1 - Sep 15", "███████████████"),
        ("  Project Planning", "Aug 1 - Aug 15", "██████"),
        ("  Requirements Analysis", "Aug 10 - Aug 25", "      ████████"),
        ("  Technology Research", "Aug 20 - Sep 5", "            ████████"),
        ("  System Design", "Aug 25 - Sep 15", "              ██████████"),
        ("", "", ""),
        ("Backend Development", "Sep 1 - Oct 15", "         ████████████████████"),
        ("  Database Schema", "Sep 1 - Sep 10", "         █████"),
        ("  Models Implementation", "Sep 10 - Sep 20", "              █████"),
        ("  Data Collectors", "Sep 15 - Oct 5", "                ████████"),
        ("  Financial Algorithms", "Sep 20 - Oct 10", "                  ████████"),
        ("  Portfolio Optimization", "Sep 25 - Oct 8", "                    ██████"),
        ("  API Server", "Oct 1 - Oct 15", "                      ███████"),
        ("", "", ""),
        ("Frontend Development", "Oct 5 - Nov 5", "                     ████████████████"),
        ("  React Setup", "Oct 5 - Oct 8", "                     ██"),
        ("  UI Components", "Oct 8 - Oct 12", "                       ██"),
        ("  Authentication", "Oct 10 - Oct 18", "                        ████"),
        ("  Dashboard", "Oct 15 - Oct 25", "                           █████"),
        ("  Portfolio Interface", "Oct 18 - Oct 28", "                            █████"),
        ("  Charts & Analytics", "Oct 22 - Nov 2", "                              ██████"),
        ("  Notifications", "Oct 25 - Nov 5", "                                ██████"),
        ("", "", ""),
        ("Testing & Integration", "Oct 28 - Nov 20", "                              ███████████"),
        ("  Integration", "Oct 28 - Nov 8", "                              ██████"),
        ("  Unit Testing", "Nov 1 - Nov 12", "                                ██████"),
        ("  Integration Testing", "Nov 5 - Nov 15", "                                  █████"),
        ("  Performance Testing", "Nov 8 - Nov 18", "                                    █████"),
        ("  Security Testing", "Nov 10 - Nov 20", "                                     █████"),
        ("", "", ""),
        ("Deployment & Docs", "Nov 12 - Dec 10", "                                   ██████████████"),
        ("  Migration Scripts", "Nov 12 - Nov 18", "                                   ███"),
        ("  Production Setup", "Nov 15 - Nov 22", "                                     ████"),
        ("  Documentation", "Nov 18 - Nov 30", "                                       ██████"),
        ("  Report Writing", "Nov 25 - Dec 10", "                                          ████████"),
        ("  Final Testing", "Nov 28 - Dec 5", "                                            ████"),
        ("  Presentation Prep", "Dec 1 - Dec 8", "                                              ████"),
        ("  Project Submission", "Dec 8 - Dec 10", "                                                ██"),
    ]
    
    print("\nTask Timeline:")
    print("Aug    Sep    Oct    Nov    Dec")
    print("|      |      |      |      |")
    
    for task_name, duration, visual in tasks:
        if task_name:
            print(f"{task_name:<25} {duration:<15} {visual}")
        else:
            print()
    
    print("\n" + "="*80)
    print("Legend: █ = Active Period")
    print("Total Duration: 131 days (August 1 - December 10, 2024)")
    print("="*80)

if __name__ == "__main__":
    print("🚀 Generating Lumia Gantt Charts...")
    
    # Generate text version
    print_text_gantt()
    
    # Generate visual version
    try:
        fig = create_simple_gantt_chart()
        print("📊 Visual Gantt chart generated successfully!")
    except Exception as e:
        print(f"⚠️  Visual chart generation failed: {e}")
        print("💡 Text version generated above.")
    
    print("\n✨ Gantt chart generation complete!")
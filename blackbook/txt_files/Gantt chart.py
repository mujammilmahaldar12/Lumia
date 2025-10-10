#!/usr/bin/env python3
"""
Lumia Robo-Advisor - Gantt Chart Generator
Generates a professional Gantt chart for the project timeline
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def create_lumia_gantt_chart():
    """
    Create a comprehensive Gantt chart for Lumia Robo-Advisor project
    """
    
    # Project data
    tasks = [
        # Initial Planning Phase
        {"task": "Project Planning", "start": "2024-08-01", "end": "2024-08-15", "phase": "Planning", "color": "#87CEEB"},
        {"task": "Requirements Analysis", "start": "2024-08-10", "end": "2024-08-25", "phase": "Planning", "color": "#90EE90"},
        {"task": "Technology Research", "start": "2024-08-20", "end": "2024-09-05", "phase": "Planning", "color": "#FFFF00"},
        {"task": "System Design", "start": "2024-08-25", "end": "2024-09-15", "phase": "Planning", "color": "#FFA500"},
        
        # Phase 1: Backend Development
        {"task": "Database Schema Design", "start": "2024-09-01", "end": "2024-09-10", "phase": "Backend", "color": "#FFC0CB"},
        {"task": "Database Models Implementation", "start": "2024-09-10", "end": "2024-09-20", "phase": "Backend", "color": "#E0FFFF"},
        {"task": "Data Collectors Development", "start": "2024-09-15", "end": "2024-10-05", "phase": "Backend", "color": "#EE82EE"},
        {"task": "Financial Algorithms Implementation", "start": "2024-09-20", "end": "2024-10-10", "phase": "Backend", "color": "#FFA07A"},
        {"task": "Portfolio Optimization Module", "start": "2024-09-25", "end": "2024-10-08", "phase": "Backend", "color": "#F0E68C"},
        {"task": "API Server Development", "start": "2024-10-01", "end": "2024-10-15", "phase": "Backend", "color": "#B0C4DE"},
        
        # Phase 2: Frontend Development
        {"task": "React Project Setup", "start": "2024-10-05", "end": "2024-10-08", "phase": "Frontend", "color": "#00FF00"},
        {"task": "UI Component Library Integration", "start": "2024-10-08", "end": "2024-10-12", "phase": "Frontend", "color": "#00FFFF"},
        {"task": "Authentication System", "start": "2024-10-10", "end": "2024-10-18", "phase": "Frontend", "color": "#FF00FF"},
        {"task": "Dashboard Development", "start": "2024-10-15", "end": "2024-10-25", "phase": "Frontend", "color": "#C0C0C0"},
        {"task": "Portfolio Generation Interface", "start": "2024-10-18", "end": "2024-10-28", "phase": "Frontend", "color": "#FFD700"},
        {"task": "Performance Charts & Analytics", "start": "2024-10-22", "end": "2024-11-02", "phase": "Frontend", "color": "#FFB6C1"},

        # Phase 3: Integration & Testing
        {"task": "Frontend-Backend Integration", "start": "2024-10-28", "end": "2024-11-08", "phase": "Testing", "color": "#9370DB"},
        {"task": "Unit Testing", "start": "2024-11-01", "end": "2024-11-12", "phase": "Testing", "color": "#CD5C5C"},
        {"task": "Integration Testing", "start": "2024-11-05", "end": "2024-11-15", "phase": "Testing", "color": "#8FBC8F"},
        {"task": "Performance Testing", "start": "2024-11-08", "end": "2024-11-18", "phase": "Testing", "color": "#BC8F8F"},
        {"task": "Security Testing", "start": "2024-11-10", "end": "2024-11-20", "phase": "Testing", "color": "#F4A460"},
        
        # Phase 4: Deployment & Documentation
        {"task": "Database Migration Scripts", "start": "2024-11-12", "end": "2024-11-18", "phase": "Deployment", "color": "#98FB98"},
        {"task": "Production Environment Setup", "start": "2024-11-15", "end": "2024-11-22", "phase": "Deployment", "color": "#ADD8E6"},
        {"task": "User Documentation", "start": "2024-11-18", "end": "2024-11-28", "phase": "Deployment", "color": "#F0E68C"},
        {"task": "Technical Documentation", "start": "2024-11-20", "end": "2024-11-30", "phase": "Deployment", "color": "#F5DEB3"},
        {"task": "Project Report Writing", "start": "2024-11-25", "end": "2024-12-10", "phase": "Deployment", "color": "#E6E6FA"},
        {"task": "Final Testing & Bug Fixes", "start": "2024-11-28", "end": "2024-12-05", "phase": "Deployment", "color": "#FFE4E1"},
        {"task": "Project Presentation Preparation", "start": "2024-12-01", "end": "2024-12-08", "phase": "Deployment", "color": "#FFFACD"},
        {"task": "Project Submission", "start": "2024-12-08", "end": "2024-12-10", "phase": "Deployment", "color": "#FF0000"},
    ]
    
    # Milestones
    milestones = [
        {"name": "Requirements Complete", "date": "2024-08-25", "color": "#FF4500"},
        {"name": "System Design Complete", "date": "2024-09-15", "color": "#FF4500"},
        {"name": "Backend MVP Complete", "date": "2024-10-15", "color": "#FF4500"},
        {"name": "Frontend MVP Complete", "date": "2024-11-05", "color": "#FF4500"},
        {"name": "Integration Complete", "date": "2024-11-20", "color": "#FF4500"},
        {"name": "Project Complete", "date": "2024-12-10", "color": "#FF0000"},
    ]
    
    # Convert to DataFrame
    df = pd.DataFrame(tasks)
    df['start'] = pd.to_datetime(df['start']).dt.date
    df['end'] = pd.to_datetime(df['end']).dt.date
    df['duration'] = (pd.to_datetime(df['end']) - pd.to_datetime(df['start'])).dt.days
    
    # Convert back to datetime for plotting
    df['start_dt'] = pd.to_datetime(df['start'])
    df['end_dt'] = pd.to_datetime(df['end'])
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Plot tasks
    for i, task in df.iterrows():
        start_date = task['start_dt']
        duration = task['duration']
        
        # Create bar for each task
        ax.barh(i, duration, left=mdates.date2num(start_date), height=0.6, 
               color=task['color'], alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Add task name - shorter text for better fit
        task_name = task['task']
        if len(task_name) > 25:
            task_name = task_name[:22] + "..."
        
        ax.text(mdates.date2num(start_date) + duration/2, i, task_name, 
               ha='center', va='center', fontsize=7, fontweight='bold')
    
    # Add milestones
    for milestone in milestones:
        milestone_date = pd.to_datetime(milestone['date'])
        ax.axvline(x=mdates.date2num(milestone_date), color=milestone['color'], 
                  linestyle='--', linewidth=2, alpha=0.7)
        ax.text(mdates.date2num(milestone_date), len(tasks), milestone['name'], 
               rotation=45, ha='right', va='bottom', fontsize=8, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Customize the chart
    ax.set_ylim(-0.5, len(tasks) + 2)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([task['task'] for task in tasks], fontsize=8)
    ax.invert_yaxis()
    
    # Format x-axis (dates)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=7))
    
    # Rotate date labels
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add grid
    ax.grid(True, axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.grid(True, axis='y', alpha=0.2, linestyle='-', linewidth=0.5)
    
    # Add phase separators and labels
    phases = df['phase'].unique()
    phase_colors = {
        'Planning': '#E6F3FF',
        'Backend': '#FFE6E6', 
        'Frontend': '#E6FFE6',
        'Testing': '#FFFFE6',
        'Deployment': '#F0E6FF'
    }
    
    current_phase = None
    phase_start = 0
    
    for i, task in df.iterrows():
        if task['phase'] != current_phase:
            if current_phase is not None:
                # Add background color for previous phase
                ax.axhspan(phase_start-0.5, i-0.5, alpha=0.1, 
                          color=phase_colors.get(current_phase, '#FFFFFF'))
            current_phase = task['phase']
            phase_start = i
    
    # Add last phase
    if current_phase is not None:
        ax.axhspan(phase_start-0.5, len(tasks)-0.5, alpha=0.1, 
                  color=phase_colors.get(current_phase, '#FFFFFF'))
    
    # Chart title and labels
    plt.title('Lumia Robo-Advisor - Project Timeline\nComprehensive Development Schedule', 
             fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Timeline (2024)', fontsize=12, fontweight='bold')
    plt.ylabel('Project Tasks', fontsize=12, fontweight='bold')
    
    # Add legend for phases
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.3, label=phase) 
                      for phase, color in phase_colors.items()]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    # Adjust layout without tight_layout
    plt.subplots_adjust(left=0.25, right=0.95, top=0.92, bottom=0.15)
    
    # Save the chart
    plt.savefig('lumia_gantt_chart.png', dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    plt.savefig('lumia_gantt_chart.pdf', bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    
    # Show the chart
    plt.show()
    
    print("✅ Gantt chart generated successfully!")
    print("📊 Files saved:")
    print("   - lumia_gantt_chart.png (High resolution image)")
    print("   - lumia_gantt_chart.pdf (Vector format)")
    
    return fig, ax

def generate_project_statistics():
    """
    Generate project statistics and timeline analysis
    """
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2024, 12, 10)
    total_days = (end_date - start_date).days
    total_weeks = total_days // 7
    
    print("\n📈 PROJECT STATISTICS")
    print("=" * 50)
    print(f"Project Duration: {total_days} days ({total_weeks} weeks)")
    print(f"Start Date: {start_date.strftime('%B %d, %Y')}")
    print(f"End Date: {end_date.strftime('%B %d, %Y')}")
    print(f"Total Tasks: 28")
    print(f"Development Phases: 4")
    print(f"Milestones: 6")
    
    # Phase breakdown
    phases = {
        'Planning': 4,
        'Backend Development': 6,
        'Frontend Development': 7,
        'Integration & Testing': 5,
        'Deployment & Documentation': 8
    }
    
    print(f"\n📋 PHASE BREAKDOWN:")
    for phase, count in phases.items():
        print(f"   {phase}: {count} tasks")

if __name__ == "__main__":
    print("🚀 Generating Lumia Robo-Advisor Gantt Chart...")
    print("=" * 60)
    
    # Generate statistics
    generate_project_statistics()
    
    # Create the Gantt chart
    fig, ax = create_lumia_gantt_chart()
    
    print("\n✨ Chart generation complete!")
    print("📝 Ready for project documentation and presentations.")

from tasks.example_task import example_navigation, manage_screenshots
import argparse
import importlib.util
import sys

# Check if wallpaper_task exists and can be imported
try:
    from tasks.wallpaper_task import wallpaper_site_visit, run_multiple_visits
    HAVE_WALLPAPER_TASK = True
except ImportError as e:
    print(f"Wallpaper task not available: {e}")
    HAVE_WALLPAPER_TASK = False

def main():
    parser = argparse.ArgumentParser(description='Advanced Automation System')
    parser.add_argument('--task', type=str, default='example', help='Task to run (example, wallpaper, multiple_visits, screenshots)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--screenshot-action', type=str, default='list', help='Screenshot action (list, clean)')
    parser.add_argument('--session-id', type=str, help='Session ID for screenshot management')
    parser.add_argument('--no-proxy', action='store_true', help='Disable proxy usage')
    
    # Add arguments for wallpaper tasks if available
    if HAVE_WALLPAPER_TASK:
        parser.add_argument('--visits', type=int, default=5, help='Number of visits for multiple_visits task')
        parser.add_argument('--delay', type=int, default=30, help='Delay between visits in seconds')
    
    args = parser.parse_args()
    
    if args.task == 'example':
        example_navigation()
    elif args.task == 'wallpaper' and HAVE_WALLPAPER_TASK:
        wallpaper_site_visit(use_proxy=not args.no_proxy)
    elif args.task == 'multiple_visits' and HAVE_WALLPAPER_TASK:
        run_multiple_visits(num_visits=args.visits, delay_between=args.delay, use_proxy=not args.no_proxy)
    elif args.task == 'screenshots':
        manage_screenshots(action=args.screenshot_action, filter_session=args.session_id)
    else:
        print(f"Unknown task: {args.task}")
        if args.task in ['wallpaper', 'multiple_visits'] and not HAVE_WALLPAPER_TASK:
            print("Note: Wallpaper tasks require wallpaper_task.py in the tasks directory")

if __name__ == "__main__":
    main()
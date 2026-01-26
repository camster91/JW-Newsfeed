"""
JW-Newsfeed Update and Publish Script
Runs the parser and publishes the feed to GitHub Pages
"""
import subprocess
import os
import sys

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"{description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        return False
    if result.stdout:
        print(f"  {result.stdout.strip()}")
    return True

def main():
    # Step 1: Run the parser
    print("=" * 50)
    print("JW-Newsfeed Update and Publish")
    print("=" * 50)

    result = subprocess.run([sys.executable, "jw_news_parser.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print("Parser failed!")
        return 1

    # Step 2: Check if feed was updated
    status = subprocess.run(["git", "status", "--porcelain", "jw_feed.xml"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("No changes to feed.")
        return 0

    # Step 3: Commit to main branch
    run_command("git add jw_feed.xml history.json", "Staging files")
    run_command('git commit -m "Auto-update RSS feed"', "Committing to main")
    run_command("git push origin main", "Pushing to main")

    # Step 4: Update gh-pages branch with just the feed
    run_command("git checkout gh-pages", "Switching to gh-pages")
    run_command("git checkout main -- jw_feed.xml", "Getting latest feed")
    run_command("git add jw_feed.xml", "Staging feed")

    # Check if there are changes to commit
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if status.stdout.strip():
        run_command('git commit -m "Update RSS feed"', "Committing to gh-pages")
        run_command("git push origin gh-pages", "Pushing to gh-pages")
    else:
        print("No changes to commit on gh-pages")

    run_command("git checkout main", "Switching back to main")

    print("=" * 50)
    print("Done! Feed published to GitHub Pages")
    print("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())

import typer
from helpers.issue_lane_verify import verify_issue

app = typer.Typer()

@app.command()
def verify(
    issue_id: str = typer.Argument(..., help="ISSUE-XXX or XXX"),
    diff: bool = typer.Option(False, "--diff", help="Fail if git diff contains files outside the Lane")
):
    raw = issue_id.strip()
    full_id = raw if raw.upper().startswith("ISSUE-") else f"ISSUE-{raw}"
    
    fails, lines = verify_issue(full_id, check_diff=diff)
    for line in lines:
        print(line)
    
    if fails:
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

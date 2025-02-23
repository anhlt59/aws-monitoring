# Contributing

## Request for changes/ Pull Requests

[Fork a repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)


## Receive remote updates

In view of staying up to date with the central repository :

```sh
git pull upstream master
```

## Choose a base branch

Before starting development, you need to know which branch to base your modifications/additions on. When in doubt, use
master.

| Type of change    |           |              Branches |
|:------------------|:---------:|----------------------:|
| Documentation     |           |              `master` |
| Bug fixes         |           |              `master` |
| New features      |           |              `master` |
| New issues models |           | `YOUR-USERNAME:patch` |

```sh
# Switch to the desired branch
git switch master

# Pull down any upstream changes
git pull

# Create a new branch to work on
git switch --create patch/1234-name-issue
```

Commit your changes, then push the branch to your fork with `git push -u fork` and open a pull request
on [the Github-issue-templates repository](https://github.com/anhlt59/aws-monitoring) following the template provided.
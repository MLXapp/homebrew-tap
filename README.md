# MLX Homebrew tap

Install [MLX Node](https://mlx.app/) with [Homebrew](https://brew.sh):

```sh
brew install mlxapp/tap/node
```

MLX Node is a menu bar app for Apple silicon Macs (macOS 14 Sonoma or later). It runs AI jobs while your Mac is idle and
finds you the best AI for it. More at [mlx.app](https://mlx.app/) and [docs.mlx.app](https://docs.mlx.app/).

`mlxapp/tap/mlx-node` installs the same app under a name that doesn't share Node.js's `node`; use either one.

## Updates

MLX Node updates itself from inside the app, so Homebrew leaves it alone (`auto_updates true`). To move a Homebrew
install to the newest version by hand:

```sh
brew upgrade --cask --greedy mlxapp/tap/node
```

## Uninstall

```sh
brew uninstall --cask mlxapp/tap/node        # removes the app
brew uninstall --cask --zap mlxapp/tap/node  # also removes its data, including this Mac's link to your wallet
```

## How the casks stay current

Every 15 minutes [a workflow](.github/workflows/update.yml) asks mlx.app for the latest public MLX Node. When there is a
new one, a Mac runner downloads it, checks its SHA-256, its Developer ID signature (team `CCKXS9W488`, bundle
`app.mlx.mac`) and Apple's notarization, installs and uninstalls it with Homebrew, and only then commits the new
version. Both cask files are written by [`.github/scripts/bump.py`](.github/scripts/bump.py).

Other ways to install: download from [mlx.app/download](https://mlx.app/download), or run
`curl -fsSL mlx.app/i | sh`.

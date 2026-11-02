cask "node" do
  version "0.18.2"
  sha256 "f9dfe3230af679ec4d305c9f770dcb769bc99a6d1368e9029aa828b7ed017a38"

  url "https://mlx.app/api/download/mac/#{version}"
  name "MLX Node"
  desc "Runs AI jobs on an idle Mac for the MLX network"
  homepage "https://mlx.app/"

  livecheck do
    url "https://mlx.app/api/download/mac/latest"
    strategy :json do |json|
      json["version"]
    end
  end

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: ">= :sonoma"

  app "MLX Node.app"

  # the same finish as `curl -fsSL mlx.app/i | sh`: no "downloaded from the Internet" question on first launch (the
  # build is notarized and its checksum is pinned above) and MLX Node opens in the menu bar
  postflight do
    system_command "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "#{appdir}/MLX Node.app"]
    system_command "/usr/bin/open", args: ["#{appdir}/MLX Node.app"] unless ENV["HOMEBREW_MLX_NO_OPEN"]
  end

  uninstall quit: "app.mlx.mac"

  zap trash: [
    "~/Library/Application Scripts/app.mlx.mac",
    "~/Library/Containers/app.mlx.mac",
  ]
end

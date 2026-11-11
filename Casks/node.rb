cask "node" do
  version "0.18.4"
  sha256 "6d2c3d4a552fffa6e71862fe0543fe338fb9a6ad19f9988daab33e3010df9725"

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

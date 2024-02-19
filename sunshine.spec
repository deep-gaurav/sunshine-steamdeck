%define commit e7eaa3ab636d8721de0869f8de527dd7b1de8a3b
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%global build_timestamp %(date +"%Y%m%d")

%global rel_build 3.git.%{build_timestamp}.%{shortcommit}%{?dist}

Name:           sunshine
Version:        0.21.0
Summary:        Sunshine is a self-hosted game stream host for Moonlight.
Release:        %{rel_build}
License:        GPLv3+
URL:            https://github.com/LizardByte/Sunshine

BuildRequires:  boost-devel
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  intel-mediasdk-devel
BuildRequires:  libappindicator-gtk3-devel
BuildRequires:  libcap-devel
BuildRequires:  libcurl-devel
BuildRequires:  libdrm-devel
BuildRequires:  libevdev-devel
BuildRequires:  libgudev
BuildRequires:  libnotify-devel
BuildRequires:  libva-devel
BuildRequires:  libvdpau-devel
BuildRequires:  libX11-devel
BuildRequires:  libxcb-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXfixes-devel
BuildRequires:  libXi-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libXrandr-devel
BuildRequires:  libXtst-devel
BuildRequires:  git
BuildRequires:  mesa-libGL-devel
BuildRequires:  miniupnpc-devel
BuildRequires:  npm
BuildRequires:  numactl-devel
BuildRequires:  openssl-devel
BuildRequires:  opus-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  rpm-build
BuildRequires:  systemd-udev
BuildRequires:  wget
BuildRequires:  which

Requires:  intel-mediasdk >= 22.3.0
Requires:  boost >= 1.81.0
Requires:  libcap >= 2.22
Requires:  libcurl >= 7.0
Requires:  libdrm > 2.4.97
Requires:  libevdev >= 1.5.6
Requires:  libopusenc >= 0.2.1
Requires:  libva >= 2.14.0
Requires:  libvdpau >= 1.5
Requires:  libwayland-client >= 1.20.0
Requires:  libX11 >= 1.7.3.1
Requires:  miniupnpc >= 2.2.4
Requires:  numactl-libs >= 2.0.14
Requires:  openssl >= 3.0.2
Requires:  pulseaudio-libs >= 10.0
Requires:  libappindicator-gtk3 >= 12.10.0


%description
Sunshine is a self-hosted game stream host for Moonlight. Offering low latency, cloud gaming server capabilities with support for AMD, Intel, and Nvidia GPUs for hardware encoding. Software encoding is also available. You can connect to Sunshine from any Moonlight client on a variety of devices. A web UI is provided to allow configuration, and client pairing, from your favorite web browser. Pair from the local server or any mobile device.


%prep
git clone --single-branch --branch nightly https://github.com/matte-schwartz/Sunshine.git
cd Sunshine
git checkout %{commit}
git submodule update --init --recursive
npm install


%build
# Set up the build directory and run cmake and make
cd Sunshine
mkdir build
cd build
cmake .. \
-DCMAKE_BUILD_TYPE=Release \
-DCMAKE_INSTALL_PREFIX=/usr \
-DSUNSHINE_ASSETS_DIR=share/sunshine \
-DSUNSHINE_EXECUTABLE_PATH=/usr/bin/sunshine \
-DSUNSHINE_ENABLE_WAYLAND=ON \
-DSUNSHINE_ENABLE_X11=ON \
-DSUNSHINE_ENABLE_DRM=ON \
-DSUNSHINE_ENABLE_CUDA=ON


%make_build


%install
cd Sunshine
cd build
%make_install
%clean

%post

#!/bin/sh

# Ensure Sunshine can grab images from KMS
path_to_setcap=$(which setcap)
if [ -x "$path_to_setcap" ] ; then
  echo "$path_to_setcap cap_sys_admin+p /usr/bin/sunshine"
	$path_to_setcap cap_sys_admin+p $(readlink -f /usr/bin/sunshine)
fi

%files
# Executables
%{_bindir}/sunshine
%{_bindir}/sunshine-0.21.0.%{shortcommit}

# Systemd unit file for user services
%{_userunitdir}/sunshine.service

# Udev rules
%{_udevrulesdir}/85-sunshine.rules

# Desktop entries
%{_datadir}/applications/sunshine.desktop
%{_datadir}/applications/sunshine_terminal.desktop

# Icons
%{_datadir}/icons/hicolor/scalable/apps/sunshine.svg
%{_datadir}/icons/hicolor/scalable/status/sunshine-locked.svg
%{_datadir}/icons/hicolor/scalable/status/sunshine-pausing.svg
%{_datadir}/icons/hicolor/scalable/status/sunshine-playing.svg
%{_datadir}/icons/hicolor/scalable/status/sunshine-tray.svg

# Metainfo
%{_datadir}/metainfo/sunshine.appdata.xml

# Main application assets and shaders
%{_datadir}/sunshine/apps.json
%{_datadir}/sunshine/box.png
%{_datadir}/sunshine/desktop-alt.png
%{_datadir}/sunshine/desktop.png
%{_datadir}/sunshine/steam.png
%dir %{_datadir}/sunshine/shaders
%dir %{_datadir}/sunshine/shaders/opengl
%{_datadir}/sunshine/shaders/opengl/*

# Web assets
%{_datadir}/sunshine/web/apps.html
%{_datadir}/sunshine/web/config.html
%{_datadir}/sunshine/web/index.html
%{_datadir}/sunshine/web/password.html
%{_datadir}/sunshine/web/pin.html
%{_datadir}/sunshine/web/troubleshooting.html
%{_datadir}/sunshine/web/welcome.html
%{_datadir}/sunshine/web/assets/*
%{_datadir}/sunshine/web/images/*



%changelog

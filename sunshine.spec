%undefine _hardened_build
%define commit bd5c50041cc020f648a45f8130ed421f2c8fc901

%global build_timestamp %(date +"%Y%m%d")

Name:           sunshine
Version:        0.22.2
Summary:        Sunshine is a self-hosted game stream host for Moonlight.
Release:        3%{?dist}
License:        GPLv3+
URL:            https://github.com/LizardByte/Sunshine

BuildRequires:  boost-devel
BuildRequires:  cmake
BuildRequires:  cuda-toolkit-12-4
BuildRequires:  doxygen
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
BuildRequires:  graphviz
BuildRequires:  mesa-libGL-devel
BuildRequires:  miniupnpc-devel
BuildRequires:  npm
BuildRequires:  numactl-devel
BuildRequires:  openssl-devel
BuildRequires:  opus-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  python3.11
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
git clone --single-branch --branch nightly https://github.com/deep-gaurav/Sunshine.git
cd Sunshine
git checkout %{commit}
git submodule update --init --recursive
npm install


%build
# Dynamically locate nvcc
export PATH=/usr/local/cuda-12.4/bin:${PATH}
export LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:${LD_LIBRARY_PATH}
NVCC_PATH=$(which nvcc)

# Set up the build directory for Sunshine and configure the build with cmake
mkdir -p %{_builddir}/Sunshine/build
cd %{_builddir}/Sunshine/build

# Configure cmake with CUDA paths and other options
%if 0%{?fedora} == 39
cmake .. \
-DCMAKE_BUILD_TYPE=Release \
-DCMAKE_INSTALL_PREFIX=%{_prefix} \
-DCMAKE_CUDA_COMPILER=$NVCC_PATH \
-DSUNSHINE_ENABLE_CUDA=ON \
-DSUNSHINE_ASSETS_DIR=%{_datadir}/sunshine \
-DSUNSHINE_EXECUTABLE_PATH=%{_bindir}/sunshine \
-DSUNSHINE_ENABLE_WAYLAND=ON \
-DSUNSHINE_ENABLE_X11=ON \
-DSUNSHINE_ENABLE_DRM=ON
%else
cmake .. \
-DCMAKE_BUILD_TYPE=Release \
-DCMAKE_INSTALL_PREFIX=%{_prefix} \
-DSUNSHINE_ASSETS_DIR=%{_datadir}/sunshine \
-DSUNSHINE_EXECUTABLE_PATH=%{_bindir}/sunshine \
-DSUNSHINE_ENABLE_WAYLAND=ON \
-DSUNSHINE_ENABLE_X11=ON \
-DSUNSHINE_ENABLE_DRM=ON
%endif
%make_build

%install
cd %{_builddir}/Sunshine/build
%make_install
%clean

%post

# Ensure Sunshine can grab images from KMS
path_to_setcap=$(which setcap)
if [ -x "$path_to_setcap" ] ; then
  echo "$path_to_setcap cap_sys_admin+p /usr/bin/sunshine"
	$path_to_setcap cap_sys_admin+p $(readlink -f /usr/bin/sunshine)
fi

# Add firewall rules to allow traffic on the required ports
if [ ! -x "$(command -v rpm-ostree)" ]; then
    # We're not in an rpm-ostree environment, proceed with firewall rules
    firewall-cmd --permanent --add-port=47984-47990/tcp
    firewall-cmd --permanent --add-port=48010/tcp
    firewall-cmd --permanent --add-port=47998-48000/udp
    firewall-cmd --reload
fi

%preun
# Remove the firewall rules if the package is being uninstalled, not upgraded
if [ ! -x "$(command -v rpm-ostree)" ] && [ $1 -eq 0 ]; then
    # We're not in an rpm-ostree environment and the package is being uninstalled, not upgraded
    firewall-cmd --permanent --remove-port=47984-47990/tcp
    firewall-cmd --permanent --remove-port=48010/tcp
    firewall-cmd --permanent --remove-port=47998-48000/udp
    firewall-cmd --reload
fi

%files
# Executables
%{_bindir}/sunshine
%{_bindir}/sunshine-%{version}.*

# Systemd unit file for user services
%{_userunitdir}/sunshine.service

# Udev rules
%{_udevrulesdir}/60-sunshine.rules

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

%global commit_linux_short ddfddf8
%global commit_linux_long  ddfddf829693c6bb739074e1b14e9e4fa1c55ea8

%define Arch arm

Name:           odroidu3-kernel
Version:        3.8.13.30
Release:        2%{dist}
Summary:        Specific kernel for Odroid U3

License:        GPLv2
URL:            http://builder.mdrjr.net/
Source0:        http://builder.mdrjr.net/kernel-3.8/16-16/odroidu2.tar.xz
Source1:        https://github.com/hardkernel/linux/tarball/%{commit_linux_long}
Source2:        http://builder.mdrjr.net/tools/firmware.tar.xz

Group:          System Environment/Kernel
Provides:       kernel = %{version}-%{release}
Requires:       dracut, uboot-tools

%description
Specific kernel for Odroid U3
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%package devel
Group:          System Environment/Kernel
Summary:        Development package for building kernel modules to match the kernel
Provides:       kernel-devel = %{version}-%{release}

%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.


%package firmware
Group:          Development/System
Summary:        Firmware files used by the Linux kernel
Provides:       kernel-firmware = %{version}-%{release}

%description firmware
Kernel-firmware includes firmware files required for some devices to
operate.


%prep
%setup -q -c
mkdir -p lib/firmware
%setup -q -D -T -n %{name}-%{version}/lib/firmware -a2
%setup -q -D -T -a1

%build
cd hardkernel-linux-%{commit_linux_short}
make mrproper
cp arch/arm/configs/odroidu_defconfig .config
make olddefconfig
make modules_prepare
cd ..
mv boot/zImage boot/zImage-%{version}-%{release}
mv boot/config-%{version} boot/config-%{version}-%{release}
mv lib/modules/%{version} lib/modules/%{version}-%{release}
rm lib/modules/%{version}-%{release}/build
rm lib/modules/%{version}-%{release}/source
cp lib/firmware/s5p-mfc/* lib/firmware

%install
mkdir -p %{buildroot}
cp -Rp boot lib %{buildroot}

# kernel-devel
DevelDir=/usr/src/kernels/%{version}-%{release}
mkdir -p %{buildroot}$DevelDir
cd hardkernel-linux-%{commit_linux_short}
# first copy everything
cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}$DevelDir
# then drop all but the needed Makefiles/Kconfig files
rm -rf %{buildroot}$DevelDir/Documentation
rm -rf %{buildroot}$DevelDir/scripts
rm -rf %{buildroot}$DevelDir/include
cp .config %{buildroot}$DevelDir
cp -a scripts %{buildroot}$DevelDir
cp -a include %{buildroot}$DevelDir

if [ -d arch/$Arch/scripts ]; then
  cp -a arch/$Arch/scripts %{buildroot}$DevelDir/arch/%{_arch} || :
fi
if [ -f arch/$Arch/*lds ]; then
  cp -a arch/$Arch/*lds %{buildroot}$DevelDir/arch/%{_arch}/ || :
fi
rm -f %{buildroot}$DevelDir/scripts/*.o
rm -f %{buildroot}$DevelDir/scripts/*/*.o
cp -a --parents arch/%{Arch}/include %{buildroot}$DevelDir
# include the machine specific headers for ARM variants, if available.
if [ -d arch/%{Arch}/mach-exynos/include ]; then
  cp -a --parents arch/%{Arch}/mach-exynos/include %{buildroot}$DevelDir
fi
cp include/generated/uapi/linux/version.h %{buildroot}$DevelDir/include/linux
touch -r %{buildroot}$DevelDir/Makefile %{buildroot}$DevelDir/include/linux/version.h
ln -s $DevelDir %{buildroot}/lib/modules/%{version}-%{release}/build


%files
%defattr(-,root,root,-)
/lib/modules/%{version}-%{release}/*
/boot/config-%{version}-%{release}
%attr(0755,root,root) /boot/zImage-%{version}-%{release}

%post
cp -a /boot/zImage-%{version}-%{release} /boot/zImage
rm -f /lib/modules/%{version}
ln -s /lib/modules/%{version}-%{release} /lib/modules/%{version}
dracut /boot/initrd-%{version}-%{release} %{version}
mkimage -A arm -O linux -T ramdisk -C none -a 0 -e 0 \
	-n "uInitrd %{version}-%{release}" \
	-d /boot/initrd-%{version}-%{release} \
	/boot/uInitrd-%{version}-%{release}
cp -a /boot/uInitrd-%{version}-%{release} /boot/uInitrd

%preun
rm -f /boot/initrd-%{version}-%{release}
rm -f /boot/uInitrd-%{version}-%{release}
rm -f /lib/modules/%{version}
if [ "$(ls -1 /lib/modules/%{version}-*|wc)" != "1" ] ; then 
    ln -s $(ls -1 /lib/modules/%{version}-* | grep -v /lib/modules/%{version}-%{release} |tail -1) /lib/modules/%{version}
fi

%postun
cp $(ls -1 /boot/uInitrd-*-*|tail -1) /boot/uInitrd
cp $(ls -1 /boot/zImage-*-*|tail -1) /boot/zImage


%files devel
%defattr(-,root,root)
/usr/src/kernels/%{version}-%{release}


%files firmware
%defattr(-,root,root)
/lib/firmware/*

%changelog
* Sun Dec 20 2015 Jacco Ligthart <jacco@redsleeve.org>
- updated to 3.8.13.30 again :( 
- apparently upstream produces multiple kernels with the same version

* Fri May 15 2015 Jacco Ligthart <jacco@redsleeve.org>
- updated to 3.8.13.30
- changed to creating -devel from source as it is no longer available as binary


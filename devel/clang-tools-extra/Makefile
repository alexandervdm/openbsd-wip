# $OpenBSD: Makefile $

# XXX
# This port is more or less a simple copy from devel/llvm and it tries to
# package the clang extra tools without to increase the complexity of
# devel/llvm.
#
# Please keep patches in sync with devel/llvm and just rmove the
# lld and lldb patches: rm patches/patch-*lld*
# The clang extra tools do not need to patch.

# XXX If broken on an architecture, remove the arch from LLVM_ARCHS.
ONLY_FOR_ARCHS = ${LLVM_ARCHS}

DPB_PROPERTIES = parallel

COMMENT=	Clang extra tools

LLVM_V =	8.0.0
DISTNAME =	llvm-${LLVM_V}.src
PKGNAME=	clang-tools-extra-${LLVM_V}

CATEGORIES =	devel

# packager notes in http://llvm.org/docs/Packaging.html
HOMEPAGE =	https://www.llvm.org/

MAINTAINER=	Jeremie Courreges-Anglas <jca@wxcvbn.org>

# BSD
PERMIT_PACKAGE =	Yes

WANTLIB += ${COMPILER_LIBCXX} c curses edit m z

# patches patch-tools_lld
MASTER_SITES =	https://releases.llvm.org/${LLVM_V}/
EXTRACT_SUFX =	.tar.xz
DISTFILES =	llvm-${LLVM_V}.src${EXTRACT_SUFX} \
		cfe-${LLVM_V}.src${EXTRACT_SUFX} \
		clang-tools-extra-${LLVM_V}.src${EXTRACT_SUFX}

COMPILER =		base-clang ports-gcc

MODULES =		devel/cmake \
			lang/python

BUILD_DEPENDS +=	devel/swig \
			textproc/py-recommonmark

RUN_DEPENDS +=		devel/gtest \
			devel/llvm

.include <bsd.port.arch.mk>

.if !${PROPERTIES:Mclang}
TEST_DEPENDS +=		lang/gcc/${MODGCC4_VERSION},-c++
RUN_DEPENDS +=		lang/gcc/${MODGCC4_VERSION},-c++
.endif

CONFIGURE_STYLE =	cmake

# Disable the most stuff to speed up the whole build step
CONFIGURE_ARGS =	-DLLVM_ENABLE_FFI=OFF \
			-DLLVM_ENABLE_TERMINFO=ON \
			-DLLVM_ENABLE_RTTI=ON \
			-DCMAKE_DISABLE_FIND_PACKAGE_LibXml2=ON \
			-DLLVM_LINK_LLVM_DYLIB=OFF \
			-DLLVM_BUILD_LLVM_DYLIB=OFF \
			-DGO_EXECUTABLE=GO_EXECUTABLE-NOTFOUND \
			-DBacktrace_LIBRARY=''

CONFIGURE_ARGS +=	-DCLANG_ENABLE_STATIC_ANALYZER=ON \
			-DCLANG_INCLUDE_TESTS=OFF \
			-DLLVM_BUILD_TESTS=OFF \
			-DLLVM_BUILD_BENCHMARKS=OFF \
			-DLLVM_ENABLE_DOXYGEN=OFF \
			-DLLVM_ENABLE_SPHINX=OFF \
			-DLLVM_INCLUDE_EXAMPLES=OFF \
			-DLLVM_INCLUDE_TESTS=OFF \
			-DLLVM_INCLUDE_BENCHMARKS=OFF

# Disable some protections in the compiler to regain performance
.if ${MACHINE_ARCH} == "aarch64" || ${MACHINE_ARCH} == "amd64" || \
    ${MACHINE_ARCH} == "i386"
CXXFLAGS +=	-fno-ret-protector
.endif
.if ${MACHINE_ARCH} == "amd64" || ${MACHINE_ARCH} == "i386"
CXXFLAGS +=	-mno-retpoline
.endif

# Workaround relocation overflow
.if ${MACHINE_ARCH} == "powerpc"
# As a workaround for the size only build the PowerPC backend
CONFIGURE_ARGS +=	-DLLVM_TARGETS_TO_BUILD="PowerPC"
.elif ${MACHINE_ARCH} == "arm"
CFLAGS +=		-mlong-calls
CXXFLAGS +=		-mlong-calls
.endif

.if ${MACHINE_ARCH} == "powerpc"
PKG_ARGS +=		-Dpowerpc=1
.else
PKG_ARGS +=		-Dpowerpc=0
.endif

# XXX sync
GCC_VER =		8.3.0
.if ${MACHINE_ARCH} == "amd64"
GCC_CONFIG =		x86_64-unknown-openbsd${OSREV}
.else
GCC_CONFIG =		${MACHINE_ARCH}-unknown-openbsd${OSREV}
.endif
CLANG_INCLUDE_PATH =	lib/clang/${LLVM_V}/include
SUBST_VARS +=		CLANG_INCLUDE_PATH LLVM_V GCC_VER GCC_CONFIG

post-extract:
	mv ${WRKDIR}/cfe-${LLVM_V}.src ${WRKSRC}/tools/clang
	mv ${WRKDIR}/clang-tools-extra-${LLVM_V}.src ${WRKSRC}/tools/clang/tools/extra

pre-configure:
	@${SUBST_CMD} ${WRKSRC}/tools/clang/lib/Driver/ToolChains/OpenBSD.cpp
	-@ln -s ${MODPY_BIN} ${WRKDIR}/bin/python

post-install:
	${MODPY_BIN} ${MODPY_LIBDIR}/compileall.py \
		${PREFIX}/share/clang

# LLVM/Clang use the OpenBSD shared lib style so.X.Y. So we need this helper
# environment
.for _n _v in clang 8.0 lldb 1.0 LTO 5.0
CONFIGURE_ENV+=LIB${_n}_VERSION=${_v}
MAKE_ENV+=LIB${_n}_VERSION=${_v}
.endfor

.include <bsd.port.mk>

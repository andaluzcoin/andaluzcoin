# Copyright (c) 2023-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

include(CheckCXXSourceCompiles)
include(CheckCXXSymbolExists)

check_cxx_symbol_exists(O_CLOEXEC "fcntl.h" HAVE_O_CLOEXEC)
check_cxx_symbol_exists(fdatasync "unistd.h" HAVE_FDATASYNC)
check_cxx_symbol_exists(fork "unistd.h" HAVE_DECL_FORK)
check_cxx_symbol_exists(pipe2 "unistd.h" HAVE_DECL_PIPE2)
check_cxx_symbol_exists(setsid "unistd.h" HAVE_DECL_SETSID)

if(NOT WIN32)
  include(TestAppendRequiredLibraries)
  test_append_socket_library(core_interface)
endif()

include(TestAppendRequiredLibraries)
test_append_atomic_library(core_interface)

# Even though ::system is part of the standard library, we still check
# for it, to support building targets that don't have it, such as iOS.
check_cxx_symbol_exists(std::system "cstdlib" HAVE_STD_SYSTEM)
check_cxx_symbol_exists(::_wsystem "stdlib.h" HAVE__WSYSTEM)
if(HAVE_STD_SYSTEM OR HAVE__WSYSTEM)
  set(HAVE_SYSTEM 1)
endif()

check_cxx_source_compiles("
  #include <string.h>

  int main()
  {
    char buf[100];
    char* p{strerror_r(0, buf, sizeof buf)};
    (void)p;
  }
  " STRERROR_R_CHAR_P
)

# Check for malloc_info (for memory statistics information in getmemoryinfo).
check_cxx_symbol_exists(malloc_info "malloc.h" HAVE_MALLOC_INFO)

# Check for mallopt(M_ARENA_MAX) (to set glibc arenas).
check_cxx_source_compiles("
  #include <malloc.h>

  int main()
  {
    mallopt(M_ARENA_MAX, 1);
  }
  " HAVE_MALLOPT_ARENA_MAX
)

# Check for posix_fallocate().
check_cxx_source_compiles("
  #include <fcntl.h>

  int main()
  {
    return posix_fallocate(0, 0, 0);
  }
  " HAVE_POSIX_FALLOCATE
)

# Check for strong getauxval() support in the system headers.
check_cxx_source_compiles("
  #include <sys/auxv.h>

  int main()
  {
    getauxval(AT_HWCAP);
  }
  " HAVE_STRONG_GETAUXVAL
)

# Check for UNIX sockets.
check_cxx_source_compiles("
  #include <sys/socket.h>
  #include <sys/un.h>

  int main()
  {
    struct sockaddr_un addr;
    addr.sun_family = AF_UNIX;
  }
  " HAVE_SOCKADDR_UN
)

# Check for different ways of gathering OS randomness:
# - Linux getrandom()
check_cxx_source_compiles("
  #include <sys/random.h>

  int main()
  {
    getrandom(nullptr, 32, 0);
  }
  " HAVE_GETRANDOM
)

# - BSD getentropy()
check_cxx_source_compiles("
  #include <sys/random.h>

  int main()
  {
    getentropy(nullptr, 32);
  }
  " HAVE_GETENTROPY_RAND
)


# - BSD sysctl()
check_cxx_source_compiles("
  #include <sys/types.h>
  #include <sys/sysctl.h>

  #ifdef __linux__
  #error Don't use sysctl on Linux, it's deprecated even when it works
  #endif

  int main()
  {
    sysctl(nullptr, 2, nullptr, nullptr, nullptr, 0);
  }
  " HAVE_SYSCTL
)

# - BSD sysctl(KERN_ARND)
check_cxx_source_compiles("
  #include <sys/types.h>
  #include <sys/sysctl.h>

  #ifdef __linux__
  #error Don't use sysctl on Linux, it's deprecated even when it works
  #endif

  int main()
  {
    static int name[2] = {CTL_KERN, KERN_ARND};
    sysctl(name, 2, nullptr, nullptr, nullptr, 0);
  }
  " HAVE_SYSCTL_ARND
)

if(NOT MSVC)
  include(CheckSourceCompilesWithFlags)

  set(IS_X86_ARCH FALSE)

  if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(x86_64|AMD64|x86|i[3-6]86)$")
    set(IS_X86_ARCH TRUE)
  endif()

  # On macOS, the real target arch is controlled by CMAKE_OSX_ARCHITECTURES.
  if(APPLE AND CMAKE_OSX_ARCHITECTURES)
    set(IS_X86_ARCH FALSE)
    foreach(_arch IN LISTS CMAKE_OSX_ARCHITECTURES)
      if(_arch MATCHES "^(x86_64|x86|i[3-6]86)$")
        set(IS_X86_ARCH TRUE)
      endif()
    endforeach()
  endif()

  if(IS_X86_ARCH)
    # Check for SSE4.1 intrinsics.
    set(SSE41_CXXFLAGS -msse4.1)
    check_cxx_source_compiles_with_flags("
      #include <immintrin.h>

      int main()
      {
        __m128i a = _mm_set1_epi32(0);
        __m128i b = _mm_set1_epi32(1);
        __m128i r = _mm_blend_epi16(a, b, 0xFF);
        return _mm_extract_epi32(r, 3);
      }
      " HAVE_SSE41
      CXXFLAGS ${SSE41_CXXFLAGS}
    )

    # Check for AVX2 intrinsics.
    set(AVX2_CXXFLAGS -mavx -mavx2)
    check_cxx_source_compiles_with_flags("
      #include <immintrin.h>

      int main()
      {
        __m256i l = _mm256_set1_epi32(0);
        return _mm256_extract_epi32(l, 7);
      }
      " HAVE_AVX2
      CXXFLAGS ${AVX2_CXXFLAGS}
    )

    # Check for x86 SHA-NI intrinsics.
    set(X86_SHANI_CXXFLAGS -msse4 -msha)
    check_cxx_source_compiles_with_flags("
      #include <immintrin.h>

      int main()
      {
        __m128i i = _mm_set1_epi32(0);
        __m128i j = _mm_set1_epi32(1);
        __m128i k = _mm_set1_epi32(2);
        return _mm_extract_epi32(_mm_sha256rnds2_epu32(i, j, k), 0);
      }
      " HAVE_X86_SHANI
      CXXFLAGS ${X86_SHANI_CXXFLAGS}
    )
  else()
    set(HAVE_SSE41 FALSE)
    set(HAVE_AVX2 FALSE)
    set(HAVE_X86_SHANI FALSE)
  endif()

  # Check for ARM SHA256 intrinsics.
  set(HAVE_ARM_SHANI FALSE)
  set(ARM_SHANI_CXXFLAGS "")

  set(IS_ARM64_ARCH FALSE)
  if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(aarch64|arm64|ARM64)$")
    set(IS_ARM64_ARCH TRUE)
  endif()

  # On macOS, the actual target arch can be controlled by CMAKE_OSX_ARCHITECTURES.
  if(APPLE AND CMAKE_OSX_ARCHITECTURES)
    set(IS_ARM64_ARCH FALSE)
    foreach(_arch IN LISTS CMAKE_OSX_ARCHITECTURES)
      if(_arch MATCHES "^(arm64|aarch64)$")
        set(IS_ARM64_ARCH TRUE)
      endif()
    endforeach()
  endif()

  if(IS_ARM64_ARCH)
    set(ARM_SHANI_CXXFLAGS -march=armv8-a+crypto)
    check_cxx_source_compiles_with_flags("
      #include <arm_neon.h>

      int main()
      {
        uint32x4_t abcd = vdupq_n_u32(0);
        uint32x4_t efgh = vdupq_n_u32(1);
        uint32x4_t wk   = vdupq_n_u32(2);
        uint32x4_t r0   = vsha256hq_u32(abcd, efgh, wk);
        uint32x4_t r1   = vsha256h2q_u32(efgh, abcd, wk);
        return vgetq_lane_u32(r0, 0) + vgetq_lane_u32(r1, 0);
      }
      " HAVE_ARM_SHANI
      CXXFLAGS ${ARM_SHANI_CXXFLAGS}
    )
  endif()
endif()


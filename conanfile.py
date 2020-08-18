#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, CMake, tools

class CapicxxSomeipRuntimeConan(ConanFile):
    name = "capicxx-someip-runtime"
    version = "3.1.12.17"
    license = "https://github.com/maingig/capicxx-someip-runtime/blob/master/LICENSE"
    author = "https://github.com/maingig/capicxx-someip-runtime/blob/master/AUTHORS"
    url = "https://github.com/maingig/capicxx-someip-runtime.git"
    description = "CommonAPI C++ is a C++ framework for interprocess and network communication with SomeIP"
    topics = ("tcp", "C++", "networking")
    settings = "os", "compiler", "build_type", "arch"
    exports = "*"
    options = {
        "shared": [ True, False ],
        "fPIC": [ True, False ],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'boost:shared': False,
        'capicxx-core-runtime:shared': True,
        'vsomeip:shared': True,
    }
    generators = "cmake_find_package"

    # Custom variables
    source_url = url
    source_branch = "master"

    def requirements(self):
        self.requires("boost/1.71.0@%s/%s" % (self.user, self.channel))
        self.requires("capicxx-core-runtime/3.1.12.6@%s/%s" % (self.user, self.channel))
        self.requires("vsomeip/3.1.16.1@%s/%s" % (self.user, self.channel))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        self.run("git clone %s %s" % (self.source_url, self.name))
        self.run("cd %s && git checkout master" % (self.name))
        """Wrap the original CMake file to call conan_basic_setup
        """
        shutil.move("%s/CMakeLists.txt" % (self.name), "%s/CMakeListsOriginal.txt" % (self.name))
        f = open("%s/CMakeLists.txt" % (self.name), "w")
        f.write('cmake_minimum_required(VERSION 2.8)\n')
        f.write('set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CONAN_CXX_FLAGS}")\n')
        f.write('set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${CONAN_C_FLAGS}")\n')
        f.write('set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${CONAN_SHARED_LINKER_FLAGS}")\n')
        f.write('include(${CMAKE_SOURCE_DIR}/CMakeListsOriginal.txt)\n')
        f.close()

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_INSTALLED_COMMONAPI"] = "OFF"
        if 'fPIC' in self.options and self.options.fPIC:
            cmake.definitions["CMAKE_C_FLAGS"] = "-fPIC"
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-fPIC"
        if 'USE_FILE' in self.env and len(self.env['USE_FILE']) > 0:
            cmake.definitions["USE_FILE"] = self.env['USE_FILE']
        if 'USE_CONSOLE' in self.env and len(self.env['USE_CONSOLE']) > 0:
            cmake.definitions["USE_CONSOLE"] = self.env['USE_CONSOLE']
        if 'DEFAULT_SEND_TIMEOUT' in self.env and len(self.env['DEFAULT_SEND_TIMEOUT']) > 0:
            cmake.definitions["DEFAULT_SEND_TIMEOUT"] = self.env['DEFAULT_SEND_TIMEOUT']
        cmake.configure(source_folder=self.name, build_folder=self.name)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.name)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(['winmm', 'ws2_32'])
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(['pthread'])
        elif self.settings.os == "QNX":
            self.cpp_info.libs.extend(['socket'])

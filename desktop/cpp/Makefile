# TigerEx Desktop App - Makefile

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra
TARGET = tigerex
SRC = main.cpp

all: $(TARGET)

$(TARGET): $(SRC)
$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
rm -f $(TARGET)

run: $(TARGET)
./$(TARGET)

# For Windows (PowerShell)
win:
cl /EHsc /std:c++17 main.cpp /Fe:tigerex.exe

# For macOS
macos:
clang++ -std=c++17 -o tigerex main.cpp

.PHONY: all clean run win macos

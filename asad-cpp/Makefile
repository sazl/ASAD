
all: libasad.a

asad.o: asad.cpp asad.h
	$(CXX) -c $^

libasad.a: asad.o
	ar rcs $@ $^

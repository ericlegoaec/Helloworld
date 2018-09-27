package com.animal;

class Animal {
    Animal() {
        
    }
    void speak() {
        System.out.println("Animal");
    }
}
class Cat extends Animal {
    Cat() {
        
    }
    void speak() {
        System.out.println("Cat");
    }
}
class Giraffe extends Animal {
    Giraffe() {
        
    }
    void speak() {
        System.out.println("Giraffe");
    }
}
class Test {
    Test() {
        Cat[] cats = new Cat[]{ new Cat() };
	    Animal[] animals = cats;
	    animals[0] = new Giraffe();
        Cat cat = cats[0];
        
    }
}
public class Invariance
{
    
	public static void main(String[] args) {
		Test t = new Test();
		String[] a = new String[1];
		Object[] b = a;
		//b[0] = Integer.parseInt(1);
	}
}
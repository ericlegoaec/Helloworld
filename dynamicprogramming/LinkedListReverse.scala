import scala.collection.mutable.LinkedList


object MyApp  {
    def initLinkedListDesc(i : Int) : LinkedList[Int] = {
        if (i == 0) {
            var x = LinkedList(0)
            return x
        }
        var x = LinkedList(i)
        x.next = initLinkedListDesc(i-1)
        return x
        
    }

    def reverseLinkedList[A](x : LinkedList[A]) : LinkedList[A] = {
        if (x.next.get(0) == None) {
            return x
        }
        else {
            var y = reverseLinkedList(x)
            y.next = x
            println(y)
            return x
        }
        
    }

    def main( args: Array[String]) = {
        var x = initLinkedListDesc(10)
        // println(x.next.get(0) == None)
        println(reverseLinkedList(x))
    }
    
}

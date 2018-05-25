object Hello extends App with Test {
	def toInt(s: String):Option[Int] = {
		try {
			Some(s.toInt)
		} catch {
			case e: NumberFormatException => None
		}
	}


	sealed trait Answer
	case object Yes extends Answer
	case object No extends Answer

	val ans: Answer = Yes
	ans match {
		case Yes => println("Yes")
		case No => println("No")
	}

	var p1 = new Point(1, 2)
	println(p1.toString())

	println((0.1234) ~= (0.12345) )

	val tupleList = List[(String, String)]()

	val filtered = tupleList.takeWhile{ 
			case (s1, s2) => s1 == s2 
		}

    5 times println("Hello, world")
}

class Point(xc: Int, yc: Int) {
	val x: Int = xc
	val y: Int = yc
	def move(dx: Int, dy: Int): Point = new Point(x + dx, y + dy)
	override def toString() : String = {
		"X: " + xc.toString() + " Y: " + yc.toString()
	}
}
class ColorPoint(u: Int, v: Int, c: String) extends Point(u, v) {
	val color: String = c

	def compareWith(pt: ColorPoint): Boolean = (pt.x == x) && (pt.y == y) && (pt.color == color)
	override def move(dx: Int, dy: Int): ColorPoint = new ColorPoint(x + dy, y + dy, color)
}

trait Test {

	case class Precision(p:Double) {

	}

	implicit class DoubleWithAlmostEquals(val d:Double) {
		def ~=(d2:Double)(implicit p:Precision): Boolean = (d - d2).abs < p.p
	}

	implicit class AutoTimes(val x: Int) {
		def times[A](f: =>  A): Unit = {
			for (i <- 1 to x)
				f
		}
	}

	implicit val x: Precision = Precision(0.0001)
}
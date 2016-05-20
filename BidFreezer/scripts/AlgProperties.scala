//type=Lib
//native=true

import java.io.{File, FileInputStream}
import java.util.Properties

/**
  * Created by yijaz on 22/04/2016.
  */
class AlgProperties(file: File){
  val properties = {
    val prop = new Properties()
    prop.load(new FileInputStream(file))
    prop
  }

  def apply(field: String): String = properties.getProperty(field, null).trim
  override def toString = properties.toString
}

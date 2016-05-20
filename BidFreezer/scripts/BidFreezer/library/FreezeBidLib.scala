package BidFreezer.library

import horizontrader.services.instruments.InstrumentDescriptor

import scala.util.{Failure, Success, Try}
/**
  * Created by yijaz on 13/04/2016.
  */

trait FreezeBidLib{

  type WayToSetCapBid = (String, String, Double) => Try[Unit]
  type WayToGetFrozenBid = (String, String) => Option[Double]

  def setCapBid(wayToSetCapBid: WayToSetCapBid, wayToGetFrozenBid: WayToGetFrozenBid)(warrantInstrument: InstrumentDescriptor, context: String, atMost: Double) = {
    val productId = warrantInstrument.getKey.getUniqueId
    val targetCap = Try(wayToGetFrozenBid(productId, context)) match {
      case Success(Some(currentCap)) =>
        math.min(atMost, currentCap)
      case Success(None) =>
        atMost
      case Failure(ex) =>
        atMost
    }
    wayToSetCapBid(productId, context, targetCap)
  }

}

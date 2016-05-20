//type=Controller
//native=true

package BidFreezer

import BidFreezer.library.FreezeBidLib
import BidFreezer.message.controller.SetCapBid
import algotrader.api.Messages.{Error, Load}
import algotrader.api.NativeController
import com.hsoft.hmm.common.pricing.PricingContextNameFactory
import horizontrader.services.instruments.InstrumentDescriptor
import scala.util.{Failure, Success}

trait FreezeBidController extends NativeController with FreezeBidLib with FreezeLibControllerLib{

  val warrantInstrument : InstrumentDescriptor

  onMessage {
    case Load =>
      createSubscription[InstrumentDescriptor]("Executions", warrantInstrument)
      log.info(s"FreezeBid strategy launched for ${warrantInstrument.getUniqueId}")

    case capBid: SetCapBid =>
      log.info(s"Received controller message: $capBid for warrant ${warrantInstrument.getUniqueId}")
      val setCapBidFor = setCapBid(setCapBidWithStreamerService, getFrozenBidPriceFromStore) _
      setCapBidFor(warrantInstrument, PricingContextNameFactory.DEFAULT_CONTEXT, capBid.atMost) match {
        case Success(()) => log.info(s"Succeeded in capping bid of $warrantInstrument")
        case Failure(ex) =>
          log.error(s"Failed in capping bid of $warrantInstrument", ex)
          showError(s"Failed in capping bid of $warrantInstrument", ex)
      }

    case exceptionMessage: Error =>
      log.error(s"${exceptionMessage.from} throws exception", exceptionMessage.cause)
      showError(s"${exceptionMessage.from} throws exception", exceptionMessage.cause)
  }
}
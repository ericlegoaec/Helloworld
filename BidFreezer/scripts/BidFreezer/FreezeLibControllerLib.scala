package BidFreezer

import algotrader.api.ScriptSDK
import com.hsoft.hmm.broker.api.tables.StoreMappings
import com.hsoft.hmm.broker.api.tables.Tbl_ManualPriceOverride.Record
import horizontrader.plugins.hmm.connections.service.StoreSelectionFactoryProvider
import horizontrader.plugins.hmm.services.pricing.PriceStreamerService

import scala.util.{Failure, Success, Try}

trait FreezeLibControllerLib extends ScriptSDK {

  def setCapBidWithStreamerService(productId: String, context: String, capLevel: Double) = {
    log.info(s"Setting bid cap for $productId in $context at $capLevel")
    val pricingService = getService[PriceStreamerService]
    Try(pricingService.capBid(capLevel, productId, context))
  }

  def getFrozenBidPriceFromStore(productId: String, context: String): Option[Double] = {
    val record = Try{
      val selectionFactory = getService[StoreSelectionFactoryProvider].getStoreSelectionFactory
      val store = selectionFactory.getStoreSelection(StoreMappings.MANUAL_PRICE_OVERRIDE)
      val storePrimaryKey = s"$productId@$context"
      store.select(storePrimaryKey)
    }

    val res = record match {
      case Success(r: Record) =>
        if (r.bidMode != "REAL_TIME") Some(r.bidPrice) else None
      case Success(_) =>
        None
      case Failure(ex) =>
        log.error(s"Failed to get current bid freeze status for $productId in $context", ex)
        None
    }
    res
  }

}
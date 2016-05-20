package BidFreezer.library

import horizontrader.services.collectors.MockInstrumentManagementService
import horizontrader.services.instruments.InstrumentDescriptor
import org.scalatest.{FlatSpec, OneInstancePerTest}
import scala.util.{Success, Try}

/**
  * Created by yijaz on 03/05/2016.
  */

//todo: use SBT instead of Maven

class FreezeBidLibTest extends FlatSpec with FreezeBidLib with OneInstancePerTest{

  behavior of "WayToSetCapBid"
  val fakeConnection = "fakeConnection"
  val fakeId = "fakeId"
  val fakeName = "fakeName"
  val fakeContext = "fakeContext"
  val fakeInstrument = InstrumentDescriptor.newInstrumentDescriptor(new MockInstrumentManagementService(), fakeConnection, fakeId, fakeName)

  it  should "be called with the new cap input when the bid is not frozen" in {
    def wayToSetCapBid(productId: String, context: String, targetCap: Double): Try[Unit] = {
      assert(productId == fakeId)
      assert(context == fakeContext)
      assert(targetCap == 10.0)
      Success()
    }
    def wayToGetFrozenBid(productId: String, context: String) = None
    setCapBid(wayToSetCapBid, wayToGetFrozenBid)(fakeInstrument, fakeContext, 10.0)
  }

  it should "be called with the old cap when the new bid cap is higher than the old one" in {
    def wayToSetCapBid(productId: String, context: String, targetCap: Double): Try[Unit] = {
      assert(productId == fakeId)
      assert(context == fakeContext)
      assert(targetCap == 5.0)
      Success()
    }
    def wayToGetFrozenBid(productId: String, context: String) = Option(5.0)
    setCapBid(wayToSetCapBid,wayToGetFrozenBid)(fakeInstrument, fakeContext, 10.0)
  }

  it should "be called when with the new cap when new bid cap is lower than the old one" in {
    def wayToSetCapBid(productId: String, context: String, targetCap: Double): Try[Unit] = {
      assert(productId == fakeId)
      assert(context == fakeContext)
      assert(targetCap == 10.0)
      Success()
    }
    def wayToGetFrozenBid(productId: String, context: String) = Option(15.0)
    setCapBid(wayToSetCapBid,wayToGetFrozenBid)(fakeInstrument, fakeContext, 10.0)
  }

  it should "be called with the new cap input when cannot read old bid" in {
    def wayToSetCapBid(productId: String, context: String, targetCap: Double): Try[Unit] = {
      assert(productId == fakeId)
      assert(context == fakeContext)
      assert(targetCap == 10.0)
      Success()
    }
    def wayToGetFrozenBid(productId: String, context: String) = throw new RuntimeException("Fake Exception")
    setCapBid(wayToSetCapBid, wayToGetFrozenBid)(fakeInstrument, fakeContext, 10.0)
  }

  it should "throw when with the cap cannot be set" in {
    def wayToSetCapBid(productId: String, context: String, targetCap: Double): Try[Unit] = {
      def horizonLibraryCode() = throw new RuntimeException("Fake Exception")
      horizonLibraryCode()
    }
    def wayToGetFrozenBid(productId: String, context: String) = Option(15.0)

    intercept[RuntimeException] {
      setCapBid(wayToSetCapBid, wayToGetFrozenBid)(fakeInstrument, fakeContext, 10.0)
    }
  }
}

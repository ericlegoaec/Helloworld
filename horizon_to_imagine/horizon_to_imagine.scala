import java.time.LocalDate
import java.time.format.DateTimeFormatter

/**
* Created by kyyu on 3/5/2016.
*/
object BuySell extends Enumeration {
  val Buy = Value("Buy")
  val Sell = Value("Sell")
}
case class HoldingSecurity (
                             val secName: String,
                             val secId: String,
                             val sedol: String = "",
                             val cusip: String = "") {
  override def toString = s"$secName,$secId"

}

case class Holding(
                    val id : String= "",
                    val holdingSecurity : HoldingSecurity,
                    val account: String,
                    val group : String,
                    val customer : String = "Haitong",
                    val trader: String = "Haitong",
                    val legalEntity : String = "Haitong")

case class Trade(
                  val holding: Holding,
                  val execPrice: Double,
                  val execQty: Double,
                  val execDate: LocalDate,
                  val settleDate: Option[LocalDate] = None
                  )

object TradeConverter {

  val priceFormatter = new java.text.DecimalFormat("#.###")
  def formatPrice(price: Double) = priceFormatter.format(price)

  def optionExpiryMYToDateString(my: String): String = {
    require(my.length == 2)
    // Ref: https://www.hkex.com.hk/eng/prod/drprod/so/holidayex2.htm
    my match {
      case "C6" | "O6" => "03/30/16"
      case "D6" | "P6" => "04/28/16"
      case "E6" | "Q6" => "05/30/16"
      case "F6" | "R6" => "06/29/16"
      case "G6" | "S6" => "07/28/16"
      case "H6" | "T6" => "08/30/16"
      case "I6" | "U6" => "09/29/16"
      case "J6" | "V6" => "10/28/16"
      case "K6" | "W6" => "11/29/16"
      case "L6" | "X6" => "12/29/16"
      case _ => throw new Exception(s"unknown expiry ${my}")
    }
  }

  def optionLetterToCallPut(letter: Character): Character = if (letter >= 'A' && letter <= 'L') 'C' else if (letter >= 'M' && letter <= 'Z') 'P' else throw new IllegalArgumentException()

  val StockCodePatern = "^(\\d{1,4})@XHKG$".r
  val WarrantOrCBBCPatern = "^(\\d{5})@XHKG$".r
  val FutureCodePatern = "^([A-Z0-9]{3})([FGHJKLMNQUVXZ])(\\d)@XHKF$".r
  val OptionPatern = "^([A-Z0-9]{3})(\\d*\\.\\d+|\\d+)([CDEFGHIJKLOPQRSTUVWX])(\\d)@XHKF$".r


def horizonCodeToHoldingSec(horizonCode: String): HoldingSecurity =
  horizonCode match {
    case StockCodePatern(sCode) => HoldingSecurity(secName = "", secId = "\"" + s"#FIND_SMID_BY_ALIAS('BB Ticker', '$sCode HK Equity')" + "\"")
    case WarrantOrCBBCPatern(wCode) => HoldingSecurity(secName = "", secId = "\""  + s"#FIND_SMID_BY_ALIAS('BB Ticker', '$wCode HK Equity AVOP')"+ "\"")
    case FutureCodePatern("HSI", m, y) => HoldingSecurity(secName=s"HSI${m}${y}-1$y", secId = "")
    case FutureCodePatern("MHI", m, y) => HoldingSecurity(secName=s"HMH${m}${y}-1$y", secId = "")
    case FutureCodePatern("HHI", m, y) => HoldingSecurity(secName=s"HCEI${m}${y}-1$y", secId = "")
    case FutureCodePatern("MCH", m, y) => HoldingSecurity(secName=s"HMCE${m}${y}-1$y", secId = "")
    case FutureCodePatern(hkatsCode, m, y) => HoldingSecurity(secName = "", secId =  "\"" + s"#FIND_SMID_BY_ALIAS('BB Ticker', '${FutureCodes.localExchangeCode(hkatsCode)}=$m$y HK Equity')" + "\"")
    case OptionPatern(hkatsCode, strike, m, y) => {


        if (Set("HHI","HSI","MHI","MCH")(hkatsCode)) {
          val securityIds= Map("HSI"->"HSI", "HHI" ->"HCEI", "MHI" -> "HMH", "MCH" -> "HMCE")

          val secIdBase = securityIds(hkatsCode)
          val expiryString = optionExpiryMYToDateString(s"$m$y")

          HoldingSecurity(secName = s"$secIdBase${"%05d".format(strike toInt)}$m$y.HF-16", secId = "")
      } else {
          val secIdBase = FutureCodes.localExchangeCode(hkatsCode)
          val expiryString = optionExpiryMYToDateString(s"$m$y")
          val callPut = if (m < "O") "C" else "P"
          val bbTicker = s"$secIdBase HK ${expiryString} $callPut${formatPrice(strike toDouble)} Equity"


          HoldingSecurity(secName = "", secId =  "\""  + s"#FIND_SMID_BY_ALIAS('BB Ticker', '${bbTicker}')" + "\"")
      }
    }



    //case _ => HoldingSecurity("", "")
  }



  def main(args: Array[String]): Unit = {

    println ("hldId,hldSecName,hldSecId,smSedol,smCusip,hldAcct,hldCust,hldTrader,hldGroup,hldLegalEntity,execPrice,execQty,execTradeDt,execSettleDt,execTradeTm")

    for (line <- io.Source.fromFile("C:/TEMP/IN.CSV").getLines) {
      // parse the line
      // should have the following format
      // trade date/time, productId, buy/sell, qty, price, portfolio
      val tokens = line.split(",", -1)
      val theTradeDate = LocalDate parse tokens(0)
      val holdingSec = horizonCodeToHoldingSec(tokens(1))
      val buySell = BuySell withName tokens(2)
      val qty = (tokens(3) toDouble) * (if (buySell == BuySell.Buy) 1 else -1)
      val price = tokens(4) toDouble
      val portfolio = tokens(5) trim
      val parentPortfolio = portfolio match {
        case "Hedging" | "Market Making 1" | "Market Making 2" => "ETF MM"
        case "HFT 1" | "HFT 2" | "HFT 3" | "HFT 4" => "MM HFT"
        case "CBBC Trading" | "Flow Strategy 1" | "Warrant Trading" => "Warrant"
        case "Options" => "OTC Options"
      }
      val trade = Trade(holding = Holding(holdingSecurity = holdingSec, account = parentPortfolio, group = portfolio), execPrice = price, execQty = qty, execDate = theTradeDate)
      // convert it

      val holding : Holding = trade.holding
      val security = holding.holdingSecurity
      val execDateString = trade.execDate.format(DateTimeFormatter.ofPattern("yyyyMMdd"))
      val settDateString =  if (trade.settleDate.isDefined) trade.settleDate.get.format(DateTimeFormatter.ofPattern("yyyyMMdd")) else ""
      println (s"${holding.id},${security.secName},${security.secId},${security.sedol},${security.cusip},${holding.account},${holding.customer},${holding.trader},${holding.group},${holding.legalEntity},${trade.execPrice},${trade.execQty},${execDateString},${settDateString},")

    }


  }

}


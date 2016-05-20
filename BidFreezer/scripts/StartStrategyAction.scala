//type=Action
//native=true

import horizontrader.plugins.algotrading.monitoring.service.RemoteStrategyManagementService
import horizontrader.plugins.scalascript.util.NativeAction
import horizontrader.services.instruments.InstrumentDescriptor

import scala.collection.JavaConverters._

trait StartStrategyAction extends NativeAction{
  val properties = new AlgProperties(getResource("algo.properties"))
  val serverId = properties("remote-algo-server")
  val iconPath = properties("icon-path")
  val algoName = properties("strategy-name")
  val algoDescription = properties("strategy-description")

  action.set(
     label = s"[Start $algoName] $algoDescription",
     description = s"[Start $algoName] $algoDescription",
     compatibleTypes = Seq(classOf[InstrumentDescriptor]),
     icon = getIcon(iconPath)
   )

 var selectedInstruments: Seq[InstrumentDescriptor] = Seq.empty[InstrumentDescriptor]

 override def configure(selection: Selection): Boolean = {
  selectedInstruments = selection.content[InstrumentDescriptor]
  selectedInstruments.nonEmpty
 }

 def run() {
  val remoteService = getService[RemoteStrategyManagementService]

  selectedInstruments foreach {instrument =>
    log.info(s"Loading and starting $algoName Strategy for ${instrument.getUniqueId}")
    remoteService.loadAndStartStrategy(serverId, algoName, Map(
      "warrantInstrument" -> instrument
      ).asJava
    )
  }
 }
}

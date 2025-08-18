import loggerConfig
import logging
import nimaFunctions
import concurrent.futures
import re
import concurrent.futures


#nifs_autonomos_empresas_nubelus = ['B19811983', 'B43693274', 'B15399116', 'B12512570', 'A46294492', 'B96677372', 'A47376090', 'B44845352', 'B20771747', 'B97209258', 'B98970569', 'A08000424', 'F98733926', 'B96565734', 'B56843857', 'B98237548', 'B90163510', 'B10870582', 'B97360341', 'B97691620', 'B46090478', 'E97126098', 'B46184685', 'X9206104D', 'B40579468', 'X8006597K', 'B96754841', 'B42942748', 'B56668544', 'B96008875', 'B97700819', 'B96422415', 'B97577548', 'B96235379', 'B98799059', 'B98952245', 'B98874571', 'B98541139', 'B98775109', 'B67909598', 'B46202131', 'B96150438', 'E98515422', 'X6899780X', 'B97918262', 'B46759783', 'X5899717X', 'E40595241', 'B98965106', 'B96080924', 'B96237805', 'B96033667', 'X4128683E', 'B70722277', 'B98650419', 'B46261624', 'B97935589', 'B96253174', 'E96305636', 'B97983837', 'B40644296', 'B13969142', 'B10959203', 'B96738042', 'J05340013', 'B96230917', 'X6459786Y', 'B96343447', 'B10625978', 'B96200803', 'B98619570', 'B96112156', 'X2322633R', 'B97505960', 'B98929144', 'B72959083', 'B96503818', 'B96897608', 'B46135877', 'B72876014', 'Y0475213R', 'Y7510185D', 'B96957717', 'B98648751', 'B98491848', 'B40567265', 'X5285817A', 'J01873173', 'B97088728', 'B12412763', 'X5409454S', 'B44782266', 'B56673312', 'X3531815G', 'B96710645', 'B12418133', 'Z0294214A', 'B12287603', 'B12412771', 'B98778426', 'Y0736694H', 'B67704007', 'B44998631', 'B98612831', 'B72405970', 'J12991964', 'X9138692X', 'B12877320', 'B44530111', 'B12976478', 'B44527331', 'B97834667', 'B98872351', 'B12937918', 'B12638300', 'B98658503', 'B42911057', 'B12334223', 'E96315601', 'B98933096', 'B12750873', 'X8748111S', 'B56265481', 'B46205670', 'B96304357', 'B12334025', 'E12053930', 'B98845050', 'B96718168', 'B12369344', 'B12736070', 'B98526387', 'B97273312', 'B10852317', 'B96231162', 'B96756457', 'B46177879', 'X6682229Q', 'F98547474', 'B96149935', 'B12844460', 'B40534380', 'B72819345', 'B44501963', 'B12209342', 'B12074837', 'E98853013', 'B96129630', 'B96301320', 'B96171863', 'B16786204', 'B05483821', 'X4164397V', 'B96687017', 'E96293691', 'B96141502', 'X6113661P', 'J56961816', 'B01731892', 'B12226692', 'B97615249', 'B46973335', 'B98840655', 'B96513973', 'B98109853', 'B98769821', 'X7399953W', 'J98518046', 'B44547248', 'B96432539', 'B44516011', 'B98660442', 'B10520781', 'E13994918', 'X4535770D', 'B96646526', 'X9823756L', 'B97220446', 'B46988887', 'B97974737', 'B98781479', 'B98788052', 'B46667945', 'B98954704', 'B42749671', 'B01608694', 'B12444832', 'B96491469', 'B04934451', 'B97402994', 'B97733554', 'B98630031', 'B96097654', 'B98947559', 'X7542984L', 'B56152192', 'B75466730', 'B96577333', 'Y1060657A', 'E46366514', 'B98353436', 'B96714167', 'Y1435228L', 'Z0487375X', 'Y8500008G', 'B96761713', 'B98160815', 'X6402609F', 'B12804126', 'B12331948', 'B12030763', 'B46610457', 'B46210407', 'B98678097', 'B02563823', 'B12371266', 'B46557955', 'B96187604', 'Y6535524L', 'X6248661K', 'B97728380', 'B96157953', 'B96559208', 'X6506549X', 'B16406969', 'B96148069', 'B98969264', 'B96488481', 'Y1730079X', 'B10892586', 'Y8959828P', 'B12213336', 'E98697899', 'B96426440', 'B96386693', 'B40652281', 'A46124939', 'B83667725', 'A08359960', 'B85771269', 'B79269965', 'A45395555', 'B44617579', 'J98835184', 'B05314323', 'X9055748G', 'B98653439', 'E98368947', 'B98389620', 'B56735004', 'B12533436', 'B12053377', 'B12859369', 'F12047163', 'X5419550Z', 'E12560942', 'B12673331', 'E01604974', 'B53983102', 'B98720378', 'B98284946', 'B96244801', 'B12494100', 'B96540810', 'B97074082', 'B12994596', 'B12370201', 'Y1469120D', 'B85640845', 'B05394838', 'B44627578', 'B96296090', 'B45302270', 'B87960720', 'B87120994', 'B87942892', 'B88218938', 'B12447363', 'B45896834', 'F45741048', 'B45027315', 'B12678728', 'X8107773C', 'F96461041', 'X5059397H', 'X5872910K', 'B87951489', 'X6631339W', 'B45858321', 'X3058004Q', 'B05277660', 'B05308150', 'B56313950', 'X6179858B', 'B13732805', 'B53329470', 'G45751344', 'E06893283', 'X8623906X', 'B45381696', 'B85863504', 'B45443892', 'Y3354851Q', 'X5357629D', 'J13632732', 'E45063856', 'B45852142', 'B45886868', 'X5690857J', 'X6467785R', 'E56679400', 'B42873737', 'E70914908', 'B45874468', 'B72412315', 'F13223797', 'B72404635', 'B98776776', 'B78282662', 'X8352225M', 'B46427787', 'B96130919', 'B98225006', 'E97655484', 'B53058806', 'B54890173', 'X2989389X', 'B13181235', 'B42959551', 'B78772860', 'B09783036', 'B96593371', 'B96423165', 'B88240783', 'Y3352859W', 'B72553506', 'B13229281', 'B13221163', 'J45918224', 'B72844343', 'B45771094', 'B45725819', 'B13660840', 'B86915139', 'B45554342', 'E01642768', 'B54480629', 'B82820945', 'B02929503', 'B21626650', 'B42528547', 'X6148906V', 'J56753676', 'B45303252', 'B87681805', 'B56659774', 'X7783396N', 'J02841831', 'B03846029', 'B96155643', 'B96123864', 'B98946460', 'B70895495', 'A45311347', 'B54824453', 'B54850862', 'B13925375', 'B12975256', 'B53229787', 'B87649588', 'B96340211', 'B87466165', 'B87785275', 'B56827892', 'B16037475', 'X1974987T', 'B45425493', 'E45398666', 'B13141965', 'B67670554', 'B16315202', 'B06779888']
#nifs_autonomos_nubelus = ['52743133Q', '45911699L', '52656960R', '20149971Q', '27368619E', '22583129G', '26763003L', '53051003P', '53098280C', '73545010A', '53754876N', '24390542P', '26041956E', '22630487M', '48444681B', 'X9206104D', '20835666N', 'X8006597K', '73591973T', '22686614N', '53098251Z', '73759565Z', '08999526V', '33407383K', '22551825A', '73763380B', 'X6899780X', '44881090V', '46184178V', '25400463E', 'X5899717X', '24383777M', 'X4128683E', '22571934X', '24383591A', '19848120V', '45633333E', '48582050R', '52637317T', '48583119N', '73572646Q', '53363621X', '73578598B', 'X6459786Y', '72210201E', '11129635G', '24373275Z', '22548141E', '53200127T', '23860429E', 'X2322633R', '29188286K', '04566369H', '22563388C', '29196646D', '52685638K', 'Y0475213R', 'Y7510185D', '73640419P', 'X5285817A', '73596264J', '53053746Z', 'X5409454S', 'X3531815G', '19001693J', 'Z0294214A', '20248281R', 'Y0736694H', '54776517Q', 'X9138692X', '48436746B', '19005486B', '46278839X', '18946291H', '45469765F', '53052216W', '22689961R', '54865598H', '73390901V', '20167219Z', '29182289G', '71550470T', 'X8748111S', '20434471Y', '48312648K', '20412885V', '29215276D', 'X6682229Q', '73400920P', '48758157C', '52731009J', '20992645Q', '23320542Z', '52701237A', '20828131K', '19996780M', 'X4164397V', '73573708C', '73559599X', '11129336G', '18932243T', '73555065F', '20464300G', '16647032T', '20475391D', '20470002W', 'X6113661P', '20020676G', '54600039V', '52940617E', '33463423X', '44531634T', '53362803C', 'X7399953W', '52948334B', '53256469S', '45760407K', '22550868N', '44117651V', '53256955H', 'X4535770D', '26746849B', '73558530E', '24480347K', 'X9823756L', '48412729Y', '45630922A', '25410415S', '53254033V', '53662298D', '44860422A', '25423422G', '53376228J', '19440701C', '52744053Q', '24373079W', '52703083D', '52670983V', 'X7542984L', '19997565P', 'Y1060657A', '19850768C', '03157886D', '10252182R', 'Y1435228L', 'Z0487375X', 'Y8500008G', '53363618F', 'X6402609F', '29193550H', '73941809Y', '52634406X', '53608156D', '53876745G', '20832070G', 'Y6535524L', 'X6248661K', '23315763L', '48313511X', '48441275D', '29217104C', '48436080N', 'X6506549X', '73939839Z', 'Y1730079X', 'Y8959828P', '22675722E', '48707161S', '73574135X', '19082642W', '20462333S', '26746396H', '48442707S', 'X9055748G', '20488361F', 'X5419550Z', '52538338J', '44526530W', '24374870E', 'Y1469120D', '53222648G', '07478874X', '03538080J', '24390507L', '22596915J', '20471541T', '11804990X', 'X8107773C', 'X5059397H', 'X5872910K', 'X6631339W', '09455541B', '03906969M', '06211299B', '50474496F', 'X3058004Q', '03868458L', 'X6179858B', '06209717Q', 'X8623906X', '46842031R', '51912811V', 'Y3354851Q', 'X5357629D', '03803966L', '03873683T', '07215307T', 'X5690857J', '06232197W', '20922483G', 'X6467785R', '19007667F', '52959460M', '49019515Y', '07533828V', '03833298A', '52956738C', '24343328J', '03888055C', '53623312P', '05272232B', '70349580D', '06261543T', '06253709D', '70338095R', 'X8352225M', '48436087L', 'X2989389X', '48715134F', '06277338V', '03919086R', '50474374T', '07507362R', '18950468D', '06263015T', '03821820W', 'Y3352859W', '52120768P', '70416203R', '06228979G', '03813822P', '50599757X', '03885838B', '03963262V', '03879645M', '03796692J', '52537761B', '03889931X', '04247131C', '03833285J', '06572950X', 'X6148906V', '70361036B', '03843364H', '05455480H', '21412968Z', 'X7783396N', '53056941N', '48590095L', '78395480A', '06281748B', 'X1974987T', '53431325W', '03784042J', '44838581N', '05399704V', '18946390W', '50050198J', '11128368W', '04212156M']
#nifs_nubelus = nifs_autonomos_nubelus + nifs_autonomos_empresas_nubelus

#NIFs multicentro
nif_multicentro_valencia = "B43693274"
nif_multicentro_madrid = "B86681426"
nif_multicentro_castilla = "B45578069"
nif_multicentro_cataluña = "B08173411"

def validar_nif(nif):
    """
    Valida el formato del NIF español (empresa o persona física).
    Ejemplos válidos: B86681426, 12345678B
    Lanza ValueError si el formato es incorrecto.
    """
    if not isinstance(nif, str):
        raise ValueError("El NIF debe ser una cadena de texto.")
    nif = nif.strip().upper()
    if not re.fullmatch(r"([A-Z]\d{8}|\d{8}[A-Z])", nif):
        raise ValueError(f"Formato de NIF incorrecto: {nif}")
    return True

def busqueda_NIMA_secuencial(nif):
    """
    Toma el nif y busca en las diferentes comunidades autónomas en el orden:
    Valencia, Madrid, Castilla, Cataluña.
    Devuelve un JSON con los datos o lanza una excepción con mensaje descriptivo.
    """
    try:
        validar_nif(nif)
    except ValueError as e:
        logging.error(str(e))
        return None

    for funcion_busqueda in [nimaFunctions.busqueda_NIMA_Valencia, nimaFunctions.busqueda_NIMA_Madrid,
                                nimaFunctions.busqueda_NIMA_Cataluña, nimaFunctions.busqueda_NIMA_Castilla]:
        try:
            resultado = funcion_busqueda(nif)
            if resultado:
                return resultado
        except Exception as e:
            logging.info(f"No encontrado en {funcion_busqueda.__name__}: {e}")

    logging.error("NIF no encontrado en ninguna comunidad")
    return None


# Medir el tiempo de ejecución de cada función de búsqueda por separado
# Ver la velocidad con pruebas de listas aleatorias de 1, 10 y 100. Despues ver el peor caso, que el nif no se encuentra ninguna busqueda.

# En base a esto tenemos dos opciones:
# 1. Usar los 3 a la vez y ver si se puede hacer en paralelo. (CONSUME MUCHO RECURSOS)
# 2. Usar los más rapidos primero (medir la velocidad de cada uno)

def busqueda_NIMA(nif):
    """
    Lanza las búsquedas de NIMA en Valencia, Madrid, Castilla y Cataluña en paralelo.
    Espera siempre a que termine la búsqueda de Valencia antes de devolver cualquier resultado.
    Si Valencia devuelve un resultado válido (JSON con centros), lo devuelve siempre.
    Si Valencia no devuelve nada, devuelve el primer resultado válido que llegue de las otras comunidades,
    pero solo después de que Valencia haya terminado.
    """
    try:
        validar_nif(nif)
    except ValueError as e:
        logging.error(str(e))
        return None

    comunidades = [
        ("Valencia", nimaFunctions.busqueda_NIMA_Valencia),
        #("Madrid", nimaFunctions.busqueda_NIMA_Madrid),
        #("Castilla", nimaFunctions.busqueda_NIMA_Castilla),
        #("Cataluña", nimaFunctions.busqueda_NIMA_Cataluña)
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_comunidad = {executor.submit(func, nif): nombre for nombre, func in comunidades}
        resultados = {}
        valencia_resultado = None

        for future in concurrent.futures.as_completed(future_to_comunidad):
            nombre = future_to_comunidad[future]
            try:
                resultado = future.result()
                if resultado and isinstance(resultado, dict) and resultado.get("centros") and len(resultado["centros"]) > 0:
                    resultados[nombre] = resultado
                    if nombre == "Valencia":
                        valencia_resultado = resultado
                        break  # Si Valencia tiene datos, paramos aquí
            except Exception as e:
                logging.info(f"No encontrado en {nombre}: {e}")

    # Si Valencia ha devuelto datos válidos, devuélvelos
    if valencia_resultado:
        return valencia_resultado

    # Si no, devuelve el primer resultado válido de otra comunidad
    for nombre in ["Madrid",  "Cataluña"]:
        if nombre in resultados:
            return resultados[nombre]

    logging.error("NIF no encontrado en ninguna comunidad")
    return {"error": "NIF no encontrado en ninguna comunidad"}

datos = nimaFunctions.busqueda_NIMA_Castilla("70345107K")
print(datos)
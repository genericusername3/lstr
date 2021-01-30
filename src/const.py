DEBUG = False
CONNECTION_ERROR_TEXT = (
    "Die Liege wurde nicht erkannt. Ein Neustart könnte das Problem beheben."
    if not DEBUG
    else "Liege nicht erkannt. Der Debug-Modus ist angeschaltet."
)

# AUTO GENERATED FILE - DO NOT EDIT

#' @export
deckGL <- function(id=NULL, clickInfo=NULL, controller=NULL, enableEvents=NULL, hoverInfo=NULL, initialViewState=NULL, layers=NULL, style=NULL, tooltip=NULL, viewState=NULL) {
    
    props <- list(id=id, clickInfo=clickInfo, controller=controller, enableEvents=enableEvents, hoverInfo=hoverInfo, initialViewState=initialViewState, layers=layers, style=style, tooltip=tooltip, viewState=viewState)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DeckGL',
        namespace = 'dash_deckgl',
        propNames = c('id', 'clickInfo', 'controller', 'enableEvents', 'hoverInfo', 'initialViewState', 'layers', 'style', 'tooltip', 'viewState'),
        package = 'dashDeckgl'
        )

    structure(component, class = c('dash_component', 'list'))
}

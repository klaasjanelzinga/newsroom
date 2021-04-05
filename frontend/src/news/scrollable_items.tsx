import * as React from "react"
import { createStyles, WithStyles, withStyles } from "@material-ui/core"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { RouteComponentProps } from "react-router"
import { withRouter } from "react-router-dom"
import { WithAuthHandling, withAuthHandling } from "../WithAuthHandling"
import { fromEvent, Observable } from "rxjs"
import { debounceTime, filter } from "rxjs/operators"
import LinearProgress from "@material-ui/core/LinearProgress"

const styles = createStyles({
    newsItems: {
        overflow: "auto",
        height: "100%",
    },
    noNews: {
        paddingLeft: "30px",
    },
    scrollFiller: {
        height: "1200px",
        textAlign: "center",
    },
    scrollFillerIcon: {
        height: 160,
        width: 100,
    },
    endImage: {
        width: "63%",
        marginBottom: "1200px",
    },
    nothingHereImage: {
        width: "63%",
    },
})

export interface ScrollableItem {
    reportYPosition: () => number
    scroll_to_top: () => void
    open_item: () => void
}

export interface MarkAsReadItem {
    must_be_marked_as_read: () => MarkAsReadItem | null
    confirm_marked_as_read: () => void
    item_id: () => string
}

interface ScrollableItemsProps
    extends WithAuthHandling,
        RouteComponentProps,
        WithSnackbarProps,
        WithStyles<typeof styles> {
    registerItemControl: (itemControl: ItemControl) => void
    scrollable_items: () => ScrollableItem[]
    refresh: () => void
    on_scroll?: (on_scroll$: Observable<Event>) => void
    is_loading: boolean
}

export interface ItemControl {
    goToNextItem: () => void
    goToPreviousItem: () => void
}

class ScrollableItems extends React.Component<ScrollableItemsProps> implements ItemControl {
    items_container: HTMLDivElement | null = null
    scroll_boundary: number | null = null

    constructor(props: ScrollableItemsProps) {
        super(props)
        this.props.registerItemControl(this)
    }

    componentDidMount(): void {
        if (this.props.on_scroll && this.items_container) {
            const scroll$ = fromEvent(this.items_container, "scroll").pipe(debounceTime(400))
            this.props.on_scroll(scroll$)
        }
        fromEvent(document, "keypress")
            .pipe(filter((event: Event) => (event as KeyboardEvent).key === "j"))
            .subscribe(() => this.goToNextItem())
        fromEvent(document, "keypress")
            .pipe(filter((event: Event) => (event as KeyboardEvent).key === "k"))
            .subscribe(() => this.goToPreviousItem())
        fromEvent(document, "keypress")
            .pipe(filter((event: Event) => (event as KeyboardEvent).key === "r"))
            .subscribe(() => this.props.refresh())
        fromEvent(document, "keypress")
            .pipe(filter((event: Event) => (event as KeyboardEvent).key === "o"))
            .subscribe(() => this.open_item())

        if (this.items_container) {
            this.scroll_boundary = this.items_container.getBoundingClientRect().top + 1
        }
    }

    /*****************
     * ItemControl
     ****************/
    goToNextItem(): void {
        this.props
            .scrollable_items()
            .find((scrollable_item) => scrollable_item.reportYPosition() > (this.scroll_boundary || 170))
            ?.scroll_to_top()
    }

    goToPreviousItem(): void {
        this.props
            .scrollable_items()
            .slice()
            .reverse()
            .find((scrollable_item) => scrollable_item.reportYPosition() < 100)
            ?.scroll_to_top()
    }

    open_item(): void {
        this.props
            .scrollable_items()
            .slice()
            .find((scrollable_item) => scrollable_item.reportYPosition() > 100)
            ?.open_item()
    }

    render(): JSX.Element {
        const { classes } = this.props
        const children = this.props.children as ScrollableItem[]
        return (
            <div
                className={classes.newsItems}
                ref={(t): void => {
                    this.items_container = t
                }}
            >
                {!this.props.is_loading && (
                    <span>
                        {children?.length === 0 && (
                            <div className={classes.noNews}>
                                <img
                                    className={classes.nothingHereImage}
                                    src={"/nothing-here.gif"}
                                    alt={"Nothing here..."}
                                />
                            </div>
                        )}
                        {this.props.children}
                        {children?.length > 0 && (
                            <div className={classes.scrollFiller}>
                                <img className={classes.endImage} src={"/thats-all-folks.gif"} alt={"That was all"} />
                            </div>
                        )}
                    </span>
                )}
                {this.props.is_loading && <LinearProgress />}
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(ScrollableItems))))

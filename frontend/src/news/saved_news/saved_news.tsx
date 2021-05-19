import * as React from "react"
import { RouteComponentProps, withRouter } from "react-router-dom"
import { withAuthHandling, WithAuthHandling } from "../../WithAuthHandling"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { createStyles, WithStyles } from "@material-ui/core"
import { withStyles } from "@material-ui/core/styles"
import HeaderBar from "../../headerbar/HeaderBar"
import Header from "../../user/header"
import LinearProgress from "@material-ui/core/LinearProgress"
import { Api } from "../../Api"
import ScrollableItems, { ItemControl, ScrollableItem } from "../scrollable_items"
import { SavedNewsItem, ScrollableItemsResponse } from "../../news_room_api/saved_news_api"
import SavedNewsItemView from "./saved_news_item_view"
import NewsBar from "../news_bar"

const styles = createStyles({
    newsRoot: {
        overflow: "hidden",
    },
    newsItems: {
        height: "99%",
        width: "100%",
        position: "fixed",
    },
    footer: {},
})

interface SavedNewsProps extends RouteComponentProps, WithAuthHandling, WithSnackbarProps, WithStyles<typeof styles> {}

interface SavedNewsState {
    saved_news_items: SavedNewsItem[]
    is_loading: boolean
    no_more_items: boolean
    error: string | null
}

class SavedNews extends React.Component<SavedNewsProps, SavedNewsState> {
    api: Api
    offset = 0
    limit = 30
    item_control: ItemControl | null = null
    scrollable_view_items: ScrollableItem[] = []

    state: SavedNewsState = {
        saved_news_items: [],
        is_loading: false,
        no_more_items: false,
        error: null,
    }

    constructor(props: SavedNewsProps) {
        super(props)

        this.api = new Api(props)
    }

    componentDidMount(): void {
        this.setState({ is_loading: true })
        this.fetch_saved_news_items()
    }

    fetch_saved_news_items(): void {
        if (this.state.is_loading) {
            return
        }

        this.setState({ error: null })

        const endpoint = `/saved-news?fetch_offset=${this.offset}&fetch_limit=${this.limit}`
        this.api
            .get<ScrollableItemsResponse<SavedNewsItem>>(endpoint)
            .then((saved_items_response) => {
                this.offset += saved_items_response[1].items.length
                saved_items_response[1].items.forEach((item) => (item.is_saved = true))
                this.setState({
                    saved_news_items: this.state.saved_news_items.concat(saved_items_response[1].items),
                    no_more_items: saved_items_response[1].items.length < this.limit,
                })
            })
            .catch((reason: Error) => this.setState({ error: reason.message }))
            .finally(() => {
                this.setState({ is_loading: false })
            })
    }

    refresh(): void {
        this.setState({ saved_news_items: [], is_loading: true })
        this.offset = 0
        this.fetch_saved_news_items()
    }

    register_scrollable_item(scrollable_item: ScrollableItem): void {
        this.scrollable_view_items.push(scrollable_item)
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div className={classes.newsRoot}>
                <HeaderBar />
                <Header title={"Saved News"} />
                <NewsBar
                    refresh={(): void => this.refresh()}
                    next={(): void => this.item_control?.goToNextItem()}
                    previous={(): void => this.item_control?.goToPreviousItem()}
                />

                {this.state.is_loading && <LinearProgress />}
                <div className={classes.newsItems}>
                    {!this.state.is_loading && !this.state.error && (
                        <ScrollableItems
                            registerItemControl={(control: ItemControl): void => {
                                this.item_control = control
                            }}
                            is_loading={this.state.is_loading}
                            scrollable_items={(): ScrollableItem[] => this.scrollable_view_items}
                            refresh={(): void => this.refresh()}
                        >
                            {this.state.saved_news_items.map((saved_news_item) => (
                                <SavedNewsItemView
                                    key={saved_news_item._id}
                                    saved_news_item={saved_news_item}
                                    register_scrollable_item={(item): void => this.register_scrollable_item(item)}
                                />
                            ))}
                        </ScrollableItems>
                    )}
                </div>
                {this.state.error && <h3>An error occurred. Please check back later.</h3>}
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(SavedNews))))

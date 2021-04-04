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
import NewsItemView from "../unread_news/news_item_view"
import NewsBar from "../news_bar"
import { GetNewsItemsResponse, NewsItem } from "../../news_room_api/news_item_api"
import { Observable } from "rxjs"

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

interface OldNewsProps extends RouteComponentProps, WithAuthHandling, WithSnackbarProps, WithStyles<typeof styles> {}

interface OldNewsState {
    news_items: NewsItem[]
    number_of_unread_items: number | null
    is_loading: boolean
    error: string | null
}

class OldNews extends React.Component<OldNewsProps, OldNewsState> {
    api: Api
    token: string | null = null
    item_control: ItemControl | null = null
    scrollable_view_items: ScrollableItem[] = []
    is_loading = false
    no_more_items = false

    state: OldNewsState = {
        news_items: [],
        number_of_unread_items: null,
        is_loading: false,
        error: null,
    }

    constructor(props: OldNewsProps) {
        super(props)

        this.api = new Api(props)
    }

    componentDidMount(): void {
        this.fetch_news_items()
    }

    fetch_news_items(): void {
        if (this.is_loading || this.no_more_items) {
            return
        }

        this.is_loading = true
        const endpoint_with_token = this.token ? `/news-items/read?fetch_offset=${this.token}` : "/news-items"
        this.api
            .get<GetNewsItemsResponse>(endpoint_with_token)
            .then((newsItems) => {
                this.token = newsItems[1].token
                this.no_more_items = atob(this.token) === "DONE"
                this.setState({
                    news_items: this.state.news_items.concat(newsItems[1].news_items),
                    number_of_unread_items: newsItems[1].number_of_unread_items,
                    is_loading: false,
                })
            })
            .catch((reason: Error) => this.setState({ error: reason.message }))
            .finally(() => {
                this.is_loading = false
            })
    }

    refresh(): void {
        this.setState({ news_items: [] })
        this.token = null
        this.fetch_news_items()
    }

    on_scroll(on_scroll$: Observable<Event>): void {
        /* Fetch new items if a lot is read */
        on_scroll$.subscribe(() => {
            const unread_count = this.state.news_items.filter((item) => !item.is_read).length
            if (unread_count < 12) {
                this.fetch_news_items()
            }
        })
    }

    register_scrollable_item(scrollable_item: ScrollableItem): void {
        this.scrollable_view_items.push(scrollable_item)
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div className={classes.newsRoot}>
                <HeaderBar />
                <Header title={"Old News"} />
                <NewsBar
                    refresh={(): void => this.refresh()}
                    next={(): void => this.item_control?.goToNextItem()}
                    previous={(): void => this.item_control?.goToPreviousItem()}
                    numberOfUnread={(): number => this.state.number_of_unread_items || 0}
                />

                {this.state.is_loading && <LinearProgress />}
                <div className={classes.newsItems}>
                    <ScrollableItems
                        registerItemControl={(control: ItemControl): void => {
                            this.item_control = control
                        }}
                        scrollable_items={(): ScrollableItem[] => this.scrollable_view_items}
                        refresh={(): void => this.refresh()}
                        on_scroll={(on_scroll$: Observable<Event>): void => this.on_scroll(on_scroll$)}
                    >
                        {this.state.news_items.map((news_item) => {
                            return (
                                <NewsItemView
                                    key={news_item.news_item_id}
                                    news_item={news_item}
                                    register_scrollable_item={(item): void => this.register_scrollable_item(item)}
                                />
                            )
                        })}
                    </ScrollableItems>
                </div>
                {this.state.error && <h3>An error occurred. Please check back later.</h3>}
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(OldNews))))

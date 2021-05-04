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
import ScrollableItems, { ItemControl, MarkAsReadItem, ScrollableItem } from "../scrollable_items"
import NewsItemView from "./news_item_view"
import NewsBar from "../news_bar"
import { GetNewsItemsResponse, NewsItem } from "../../news_room_api/news_item_api"
import { Observable } from "rxjs"
import { debounceTime } from "rxjs/operators"

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

interface NewsProps extends RouteComponentProps, WithAuthHandling, WithSnackbarProps, WithStyles<typeof styles> {}

interface NewsState {
    news_items: NewsItem[]
    number_of_unread_items: number
    is_loading: boolean
    error: string | null
}

class News extends React.Component<NewsProps, NewsState> {
    api: Api
    fetch_offset = 0
    fetch_limit = 30
    item_control: ItemControl | null = null
    scrollable_view_items: ScrollableItem[] = []
    mark_as_read_items: MarkAsReadItem[] = []
    no_more_items = false

    state: NewsState = {
        news_items: [],
        number_of_unread_items: 0,
        is_loading: false,
        error: null,
    }

    constructor(props: NewsProps) {
        super(props)

        this.api = new Api(props)
    }

    componentDidMount(): void {
        this.setState({ is_loading: true })
        this.fetch_news_items()
    }

    fetch_news_items(): void {
        if (this.state.is_loading || this.no_more_items) {
            return
        }

        this.setState({ error: null })

        const endpoint_with_token = `/news-items?fetch_offset=${this.fetch_offset}&fetch_limit=${this.fetch_limit}`
        this.api
            .get<GetNewsItemsResponse>(endpoint_with_token)
            .then((newsItems) => {
                this.fetch_offset += this.fetch_limit
                this.no_more_items = newsItems[1].news_items.length < this.fetch_limit
                this.setState({
                    news_items: this.state.news_items.concat(newsItems[1].news_items),
                    number_of_unread_items: newsItems[1].number_of_unread_items,
                    is_loading: false,
                })
            })
            .catch((reason: Error) => this.setState({ error: reason.message }))
            .finally(() => {
                this.setState({ is_loading: false })
            })
    }

    refresh(): void {
        this.setState({ news_items: [], is_loading: true })
        this.fetch_offset = 0
        this.no_more_items = false
        this.fetch_news_items()
    }

    on_scroll(on_scroll$: Observable<Event>): void {
        /* Mark scrolled out of view items as read */
        on_scroll$.pipe(debounceTime(1000)).subscribe((): void => {
            const mark_as_read_items = this.mark_as_read_items
                .map((mark_as_read) => mark_as_read.must_be_marked_as_read())
                .filter((mark_as_read) => mark_as_read != null)
            if (mark_as_read_items.length > 0) {
                this.api
                    .post(
                        "/news-items/mark-as-read",
                        JSON.stringify({ news_item_ids: mark_as_read_items.map((item) => item?.item_id()) })
                    )
                    .then(() => {
                        mark_as_read_items.forEach((item) => item?.confirm_marked_as_read())
                        this.setState({
                            number_of_unread_items: this.state.number_of_unread_items - mark_as_read_items.length,
                        })
                    })
                    .catch((reason) => console.error(reason))
            }
        })

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

    register_mark_as_read(mark_as_read_item: MarkAsReadItem): void {
        this.mark_as_read_items.push(mark_as_read_item)
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div className={classes.newsRoot}>
                <HeaderBar />
                <Header title={"News"} />
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
                        is_loading={this.state.is_loading}
                        on_scroll={(on_scroll$: Observable<Event>): void => this.on_scroll(on_scroll$)}
                    >
                        {this.state.news_items.map((news_item) => {
                            return (
                                <NewsItemView
                                    key={news_item._id}
                                    news_item={news_item}
                                    register_mark_as_read_item={(item): void => this.register_mark_as_read(item)}
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

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(News))))

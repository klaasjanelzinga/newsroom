import * as React from "react"
import { createStyles, WithStyles } from "@material-ui/core"
import { RouteComponentProps, withRouter } from "react-router-dom"
import { withStyles } from "@material-ui/core/styles"
import HeaderBar from "../headerbar/HeaderBar"
import Header from "../user/header"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { Api } from "../Api"
import NewsItems, { NewsItemsControl } from "./news_items"
import NewsBar from "./news_bar"
import LinearProgress from "@material-ui/core/LinearProgress"
import { WithAuthHandling, withAuthHandling } from "../WithAuthHandling"
import { GetNewsItemsResponse, GetReadNewsItemsResponse, NewsItem } from "../news_room_api/news_item_api"

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

export enum NewsVariant {
    NEWS,
    READ_NEWS,
}

export interface NewsProps extends RouteComponentProps, WithAuthHandling, WithSnackbarProps, WithStyles<typeof styles> {
    variant: NewsVariant
}

interface NewsState {
    isLoading: boolean
    isLoadingMoreItems: boolean
    newsItems: NewsItem[]
    error: string | null
    noMoreItems: boolean
    numberOfUnread: number | null
}

class News extends React.Component<NewsProps, NewsState> {
    state: NewsState = {
        isLoading: false,
        isLoadingMoreItems: false,
        newsItems: [],
        error: null,
        noMoreItems: false,
        numberOfUnread: null,
    }
    api: Api
    token: string | null = null
    newsItemsCtrl: NewsItemsControl | null

    constructor(props: NewsProps) {
        super(props)
        this.api = new Api(props)
        this.newsItemsCtrl = null
    }

    componentDidMount(): void {
        this.setState({ isLoading: true })
        this.fetchNewsItems()
    }

    registerNewsItemsControl = (newsItemCtrl: NewsItemsControl): void => {
        this.newsItemsCtrl = newsItemCtrl
    }

    fetchNewsItems(): void {
        if (this.props.variant === NewsVariant.NEWS) {
            this.fetchUnreadNewsItems()
        } else {
            this.fetchReadNewsItems()
        }
    }

    fetchUnreadNewsItems(): void {
        const endpoint = "/news-items"
        const endpoint_with_token = this.token ? `${endpoint}?fetch_offset=${this.token}` : endpoint
        this.api
            .get<GetNewsItemsResponse>(endpoint_with_token)
            .then((newsItems) => {
                const token = newsItems[1].token
                const noMoreItems = atob(token) === "DONE"
                this.token = newsItems[1].token
                this.setState({
                    newsItems: this.state.newsItems.concat(newsItems[1].news_items),
                    noMoreItems: noMoreItems,
                    numberOfUnread: newsItems[1].number_of_unread_items,
                })
            })
            .catch((reason: Error) => this.setState({ error: reason.message }))
            .finally(() => {
                this.setState({ isLoading: false, isLoadingMoreItems: false })
            })
    }

    fetchReadNewsItems(): void {
        const endpoint = "/news-items/read"
        const endpoint_with_token = this.token ? `${endpoint}?fetch_offset=${this.token}` : endpoint
        this.api
            .get<GetReadNewsItemsResponse>(endpoint_with_token)
            .then((newsItems) => {
                const token = newsItems[1].token
                const noMoreItems = atob(token) === "DONE"
                this.token = newsItems[1].token
                this.setState({
                    newsItems: this.state.newsItems.concat(newsItems[1].news_items),
                    noMoreItems: noMoreItems,
                })
            })
            .catch((reason: Error) => this.setState({ error: reason.message }))
            .finally(() => {
                this.setState({ isLoading: false, isLoadingMoreItems: false })
            })
    }

    needMoreItems = (): void => {
        const canLoad = !this.state.isLoading && !this.state.isLoadingMoreItems && !this.state.noMoreItems
        if (canLoad) {
            this.setState({ isLoadingMoreItems: true, error: null })
            this.fetchNewsItems()
        }
    }

    refreshItems = (): void => {
        if (!this.state.isLoading && !this.state.isLoadingMoreItems) {
            this.token = null
            this.setState({ isLoading: true, newsItems: [], error: null })
            this.fetchNewsItems()
        }
    }

    numberOfUnread = (): number => {
        return this.state.numberOfUnread ? this.state.numberOfUnread : 0
    }

    markAsRead = (count: number): void => {
        if (this.state.numberOfUnread) {
            this.setState({
                numberOfUnread: this.state.numberOfUnread - count,
            })
        }
    }

    markAllAsRead = (): void => {
        this.setState({
            numberOfUnread: 0,
        })
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div className={classes.newsRoot}>
                <HeaderBar />
                <Header title={"News"} />
                <NewsBar
                    numberOfUnread={this.numberOfUnread}
                    refresh={this.refreshItems}
                    next={(): void => this.newsItemsCtrl?.goToNextItem()}
                    previous={(): void => this.newsItemsCtrl?.goToPreviousItem()}
                />
                {this.state.isLoading && <LinearProgress />}
                <div className={classes.newsItems}>
                    {!this.state.isLoading && !this.state.error && (
                        <NewsItems
                            newsItems={this.state.newsItems}
                            needMoreItems={this.needMoreItems}
                            refreshRequested={this.refreshItems}
                            registerNewsItemsControl={this.registerNewsItemsControl}
                            markAsRead={this.markAsRead}
                            markAllAsRead={this.markAllAsRead}
                            monitorScroll={this.props.variant === NewsVariant.NEWS}
                        />
                    )}
                </div>
                {this.state.error && <h3>An error occurred. Please check back later.</h3>}
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(News))))

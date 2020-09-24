import * as React from "react";
import {createStyles, WithStyles, withStyles} from "@material-ui/core";
import {NewsItem} from "../user/model";
import NewsItemNode, {NewsItemControl, NewsItemDynamicFetchControl} from "./news_item";
import {debounce} from "ts-debounce";
import DoneAllIcon from '@material-ui/icons/DoneAll'
import {Api} from "../Api";
import {withSnackbar, WithSnackbarProps} from "notistack";
import {RouteComponentProps} from "react-router";
import {withRouter} from "react-router-dom";
import Typography from "@material-ui/core/Typography";
import {WithAuthHandling, withAuthHandling} from "../WithAuthHandling";

const styles = createStyles({
    newsItems: {
        overflow: "auto",
        height: "100%",
    },
    scrollFiller: {
        height: "1200px",
        textAlign: "center",
    },
    scrollFillerIcon: {
        height: 160,
        width: 100,
    },
    noNews: {
        paddingLeft: "30px",
    },
})

interface NewsItemsProps extends WithAuthHandling, RouteComponentProps, WithSnackbarProps, WithStyles<typeof styles> {
    newsItems: NewsItem[]
    monitorScroll: boolean
    needMoreItems: () => void
    refreshRequested: () => void

    registerNewsItemsControl: (newsItemsCtrl: NewsItemsControl) => void
}

export interface NewsItemsControl {
    goToNextItem: () => void
    goToPreviousItem: () => void
}

class NewsItemsNode extends React.Component<NewsItemsProps> implements NewsItemsControl {

    onScrollDebounced: () => void
    scrollEventClients: NewsItemControl[] = []
    dynamicFetchClients: NewsItemDynamicFetchControl[] = []
    api: Api
    element: Element | null = null

    constructor(props: NewsItemsProps) {
        super(props);
        this.api = new Api(props)
        this.onScrollDebounced = debounce(this.onScroll, 100);

        this.props.registerNewsItemsControl(this)
    }

    componentDidMount() {
        document.addEventListener("keypress", this.keypress)
    }

    componentWillUnmount() {
        document.removeEventListener("keypress", this.keypress)
    }

    onScroll = () => {
        this.scrollEventClients.forEach(client => client.scrollEvent())

        // Mark news-items that have isRead as is_read at the server.
        const newsItemIds = this.scrollEventClients
            .filter(client => client.isRead())
            .filter(client => !client.isReadStateIsSent())
            .map(client => {
                client.setIsReadStateIsSent(true)
                return client.newsItemId()
            })
        if (newsItemIds.length > 0) {
            this.api.post("/news-items/mark-as-read", JSON.stringify({news_item_ids: newsItemIds}))
                .catch(reason => console.error(reason))
        }

        // count all items that are scrolled out of view. Signal more items required if unread count is to low.
        const numberOfUnread = this.dynamicFetchClients.filter(client => !client.isOutOfView()).length
        if (numberOfUnread < 12) {
            this.props.needMoreItems()
        }
    }

    registerForScrollEvents = (name: NewsItemControl) => {
        if (this.props.monitorScroll)
            this.scrollEventClients.push(name)
    }

    registerForDynamicFetch = (client: NewsItemDynamicFetchControl) => {
        this.dynamicFetchClients.push(client)
    }

    keypress = (event: KeyboardEvent) => {
        if (event.key === "j") {
            this.goToNextItem()
        } else if (event.key === "k") {
            this.goToPreviousItem()
        } else if (event.key === "r") {
            this.props.refreshRequested()
        }
    }

    goToNextItem() {
        const element = this.scrollEventClients.find(client => client.reportYPosition() > 170)
        element?.scrollToTop()
        if (!element) {
            this.element?.scrollIntoView()
        }
    }

    goToPreviousItem() {
        const element = this.scrollEventClients.slice().reverse().find(client => client.reportYPosition() < 40)
        element?.scrollToTop()
    }

    render() {
        const {classes} = this.props
        return <div className={classes.newsItems} onScroll={this.onScrollDebounced}>
            {this.props.newsItems.length === 0 && <div className={classes.noNews}>
                <Typography variant="h6">
                    No news found !
                </Typography>
            </div>}
            {this.props.newsItems.length > 0 && this.props.newsItems.map(newsItem =>
                <NewsItemNode key={newsItem.news_item_id}
                              scrollEventRegistry={this.registerForScrollEvents}
                              dynamicFetchRegistry={this.registerForDynamicFetch}
                              newsItem={newsItem}/>
            )}
            {this.props.newsItems.length > 0 && <div className={classes.scrollFiller}>
                <DoneAllIcon ref={(t) => this.element = t} className={classes.scrollFillerIcon}/>
            </div>}
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(NewsItemsNode))))

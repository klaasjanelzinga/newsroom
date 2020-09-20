import * as React from "react";
import {createStyles, WithStyles} from "@material-ui/core";
import {RouteComponentProps, withRouter} from "react-router-dom";
import {withStyles} from "@material-ui/core/styles";
import UserProfile from "../user/UserProfile";
import HeaderBar from "../headerbar/HeaderBar";
import Header from "../user/header";
import {withSnackbar, WithSnackbarProps} from "notistack";
import {GetNewsItemsResponse, NewsItem} from "../user/model";
import {Api} from "../Api";
import NewsItems from "./news_items"
import NewsBar from "./news_bar";
import LinearProgress from '@material-ui/core/LinearProgress';

const styles = createStyles({
    newsRoot: {
        overflow: "hidden",
    },
    newsItems: {
        height: "99%",
        position: "fixed",
    },
    footer: {
    }
});

export enum NewsVariant {
    NEWS,
    READ_NEWS
}

export interface NewsProps extends RouteComponentProps, WithSnackbarProps, WithStyles<typeof styles> {
    userProfile: UserProfile
    variant: NewsVariant
}

interface NewsState {
    isLoading: boolean
    isLoadingMoreItems: boolean
    newsItems: NewsItem[]
    error: string | null
    noMoreItems: boolean
}

class News extends React.Component<NewsProps, NewsState> {

    state: NewsState = {
        isLoading: false,
        isLoadingMoreItems: false,
        newsItems: [],
        error: null,
        noMoreItems: false
    }
    api: Api
    token: string | null = null

    constructor(props: NewsProps) {
        super(props);
        this.api = new Api(props)
    }

    componentDidMount() {
        this.setState({isLoading: true})
        this.fetchNewsItems()
    }

    fetchNewsItems() {
        const endpoint = this.props.variant === NewsVariant.READ_NEWS ? "/news-items/read" : "/news-items"
        const endpoint_with_token = this.token ? `${endpoint}?fetch_offset=${this.token}` : endpoint
        this.api.get<GetNewsItemsResponse>(endpoint_with_token)
            .then(newsItems => {
                const token = newsItems[1].token
                const noMoreItems = atob(token) === 'DONE'
                this.token = newsItems[1].token
                this.setState({
                    newsItems: this.state.newsItems.concat(newsItems[1].news_items),
                    noMoreItems: noMoreItems,
                })
            })
            .catch((reason: Error) => this.setState({error: reason.message}))
            .finally(() => {
                this.setState({isLoading: false, isLoadingMoreItems: false});
            })
    }

    needMoreItems = () => {
        const canLoad = !this.state.isLoading && !this.state.isLoadingMoreItems && !this.state.noMoreItems
        if (canLoad) {
            this.setState({ isLoadingMoreItems: true, error: null })
            this.fetchNewsItems()
        }
    }

    refreshItems = () => {
        if (!this.state.isLoading && !this.state.isLoadingMoreItems) {
            this.token = null
            this.setState({isLoading: true, newsItems: [], error: null})
            this.fetchNewsItems()
        }
    }

    render() {
        const {classes} = this.props
        return <div className={classes.newsRoot}>
            <HeaderBar />
            <Header title={'News'} />
            <NewsBar refresh={this.refreshItems} />
            {this.state.isLoading && <LinearProgress />}
                <div className={classes.newsItems}>
                    {!this.state.isLoading && !this.state.error &&
                    <NewsItems
                        newsItems={this.state.newsItems}
                        needMoreItems={this.needMoreItems}
                        monitorScroll={this.props.variant === NewsVariant.NEWS}/>
                    }
                </div>
            {this.state.error && <h3>An error occurred. Please check back later.</h3>}
        </div>
    }
}

export default withStyles(styles)(withRouter(withSnackbar(News)));
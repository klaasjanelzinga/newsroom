import * as React from "react";
import {createStyles, WithStyles, withStyles} from "@material-ui/core";
import {NewsItem} from "../user/model";
import Grid from "@material-ui/core/Grid";

const styles = createStyles({
        domainIcon: {
            height: 14,
            verticalAlign: "middle",
            paddingRight: 4,
        },
        linkText: {
            fontSize: "smaller",
        },
    }
)

interface AlternateLinksProps extends WithStyles<typeof styles> {
    newsItem: NewsItem;
}

class AlternateLinks extends React.Component<AlternateLinksProps> {

    element: Element | null = null

    render(): JSX.Element[] {
        const {classes} = this.props
        const newsItem = this.props.newsItem
        return newsItem.alternate_links.map((alternate_link, index) => {
            const url = new URL(alternate_link)
            const domain = url.hostname
            return <Grid item xs={12} key={index}>
                <a href={alternate_link} className={classes.linkText}>
                    <img src={newsItem.alternate_favicons[index]}  className={classes.domainIcon} alt={`[${domain}]`}/>
                    {newsItem.alternate_title_links[index]}
                </a>
            </Grid>
        })
    }
}

export default withStyles(styles)(AlternateLinks)
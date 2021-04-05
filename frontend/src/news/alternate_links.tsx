import * as React from "react"
import { createStyles, Link, WithStyles, withStyles } from "@material-ui/core"
import Grid from "@material-ui/core/Grid"

const styles = createStyles({
    domainIcon: {
        height: 14,
        verticalAlign: "middle",
        paddingRight: 4,
    },
    linkText: {
        fontSize: "smaller",
    },
})

interface AlternateLinksProps extends WithStyles<typeof styles> {
    alternate_links: string[]
    alternate_favicons: string[]
    alternate_title_links: string[]
}

class AlternateLinks extends React.Component<AlternateLinksProps> {
    element: Element | null = null

    render(): JSX.Element[] {
        const { classes } = this.props
        return this.props.alternate_links.map((alternate_link, index) => {
            const url = new URL(alternate_link)
            const domain = url.hostname
            return (
                <Grid item xs={12} key={index}>
                    <Link href={alternate_link} className={classes.linkText} target="_blank" rel="noopener">
                        <img
                            src={this.props.alternate_favicons[index]}
                            className={classes.domainIcon}
                            alt={`[${domain}]`}
                        />
                        {this.props.alternate_title_links[index]}
                    </Link>
                </Grid>
            )
        })
    }
}

export default withStyles(styles)(AlternateLinks)

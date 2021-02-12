import config from './Config'
import {RouteComponentProps} from "react-router-dom";
import {WithSnackbarProps} from "notistack";
import {ErrorResponse} from "./user/model";
import {TokenBasedAuthenticator, WithAuthHandling} from "./WithAuthHandling";

interface ApiProps extends WithSnackbarProps, RouteComponentProps, WithAuthHandling {
}

export class Api {
    props: ApiProps
    authHandling: TokenBasedAuthenticator

    constructor(props: ApiProps) {
        this.props = props
        this.authHandling = props.authHandling
    }

    _headers_from(bearer_token: string| null): Headers {
        const headers: HeadersInit = new Headers()
        headers.set('Content-Type', 'application/json')
        if (bearer_token) {
            headers.set("Authorization", bearer_token)
        }
        return headers;
    }

    async _parseResponse<T>(response: Response): Promise<T> {
        if (response.status === 401) {
            this.props.history.push(`/user/signin?redirect_to=${this.props.history.location.pathname}`);
            this.props.enqueueSnackbar('You need to signin again.', {
                variant: 'warning',
            });
        } else if (response.status === 403) {
            this.props.history.push("/user/needs-approval");
            this.props.enqueueSnackbar('Approval for usage is not yet given.', {
                variant: 'warning',
            });
        } else if (response.status === 200 || response.status === 201) {
            return await response.json() as T
        }
        const bodyReason = await response.json() as ErrorResponse
        if (bodyReason?.detail)
            throw new Error(bodyReason.detail)
        throw new Error("Something in the request is wrong.")
    }

    async get<T>(endpoint: string): Promise<[number, T]> {
        const bearer_token = this.authHandling.bearer_token()
        const url = `${config.apihost}${endpoint}`
        const request = new Request(url, {
            method: 'GET',
            headers: this._headers_from(bearer_token)
        });
        const response = await fetch(request)
        return [response.status, await this._parseResponse(response)]
    }

    async post<T>(endpoint: string, body: string| null = null): Promise<[number, T]> {
        const bearer_token = this.authHandling.bearer_token()
        const url = `${config.apihost}${endpoint}`
        const response = await fetch(url, {
            headers: this._headers_from(bearer_token),
            method: "POST",
            body: body,
        })
        return [response.status, await this._parseResponse(response)]
    }
}

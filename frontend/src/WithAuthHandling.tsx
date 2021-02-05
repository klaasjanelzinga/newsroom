import * as React from 'react'
import {Subtract} from "utility-types";
import {AuthHandling} from "./index";
import config from './Config'

export interface SignInResult {
    success: boolean
    reason?: string
}

class UserInformation {
    token: string
    email_address: string
    is_approved: boolean

    constructor(token: string, email_address: string, is_approved: boolean) {
        this.token = token
        this.email_address = email_address
        this.is_approved = is_approved
    }

    static delete(): void {
        localStorage.removeItem('user-profile');
    }

    static save(user_information: UserInformation): UserInformation {
        localStorage.setItem('user-profile', JSON.stringify(user_information));
        return user_information
    }

    static load() : UserInformation | null {
        const local_storage = localStorage.getItem('user-profile')
        if (local_storage) {
            return JSON.parse(local_storage) as UserInformation
        }
        return null
    }
}

interface SignInResponse {
    token: string
    is_approved: boolean
    email_address: string
}

interface ErrorMessage {
    detail: string
}

export class TokenBasedAuthenticator {

    isSignedIn = false
    user_information: UserInformation | null = null

    static unsecure_headers(): Headers {
        const headers: HeadersInit = new Headers()
        headers.set('Content-Type', 'application/json')
        return headers
    }

    constructor() {
        this.user_information = UserInformation.load()
        if (this.user_information) {
            this.isSignedIn = true
        }
    }

    bearer_token(): string | null {
        if (!this.user_information) {
            return null
        }
        return `Bearer ${this.user_information?.token}`
    }

    async sign_in(email_address: string, password: string) : Promise<SignInResult> {
        const response = await fetch(`${config.apihost}/user/signin`, {
            headers:  TokenBasedAuthenticator.unsecure_headers(),
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                password: password,
            }),
        })

        return this._parseRequestForToken(response)
    }

    async sign_out(): Promise<void> {
        this.isSignedIn = false
        this.user_information = null
        UserInformation.delete()
        return Promise.resolve()
    }

    async change_password(email_address: string, current_password: string, new_password:string, new_password_repeated: string) : Promise<SignInResult> {
        const response = await fetch(`${config.apihost}/user/change_password`, {
            headers:  TokenBasedAuthenticator.unsecure_headers(),
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                current_password: current_password,
                new_password: new_password,
                new_password_repeated: new_password_repeated,
            }),
        })

        return this._parseRequestForToken(response)
    }

    async sign_up(email_address: string, password: string, password_repeated: string) : Promise<SignInResult> {
        const headers: HeadersInit = new Headers()
        headers.set('Content-Type', 'application/json')
        const response = await fetch(`${config.apihost}/user/signup`, {
            headers:  headers,
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                password: password,
                password_repeated: password_repeated,
            }),
        })

        return this._parseRequestForToken(response)
    }

    async _parseRequestForToken(response: Response) : Promise<SignInResult> {
        if (response.status == 200) {
            const json_response = await response.json() as SignInResponse
            this.user_information = {
                token: json_response.token,
                email_address: json_response.email_address,
                is_approved: json_response.is_approved
            }
            UserInformation.save(this.user_information)
            this.isSignedIn = true
            return Promise.resolve({
                success: true
            })
        }
        else if (response.status == 401) {
            const json_response = await response.json() as ErrorMessage
            return Promise.resolve({
                success: false,
                reason: json_response.detail
            })
        }
        return Promise.resolve({
            success: false,
            reason: "Unknown error"
        })

    }
}

export interface WithAuthHandling {
    authHandling: TokenBasedAuthenticator
}


export const withAuthHandling = <P extends WithAuthHandling>(Component: React.ComponentType<P>) =>
    class WithGoogleAuthHandler extends React.Component<Subtract<P, WithAuthHandling>> {

        render() {
            return <AuthHandling.Consumer>
                {value =>
                    <Component
                        {...this.props as P}
                        authHandling={value}
                    />
                }
            </AuthHandling.Consumer>

        }
    }

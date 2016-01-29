React = require 'react'
SubscriptionModalActions = require '../../actions/SubscriptionModalActions.coffee'


SubscribeButton = React.createClass

  _open_modal: (e) ->
    e.preventDefault()
    SubscriptionModalActions.showModal(@props.subscription_url, @props.subscription_title)

  render: ->
    return <a
      href="#"
      className="anysearch_subscribe_button"
      onClick={@_open_modal}>Suche abonnieren</a>

module.exports = SubscribeButton


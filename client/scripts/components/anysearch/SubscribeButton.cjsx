React = require 'react'


SubscribeButton = React.createClass

  render: ->
    return <form className="anysearch_subscribe_form" action="/subscribe" method="POST">
        <input type="hidden" name="subscription_url" value={@props.subscription_url} />
        <button className="anysearch_subscribe_button" onClick={@onSubscribeClicked} type="submit"></button>
      </form>

module.exports = SubscribeButton


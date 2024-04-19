# BuzzBid

##
Ally Zhang, Jay Sun, Yoga Yu

## Overview

BuzzBid is a simple online auction site that facilitates users to list and bid on items, much like existing online auction platforms but with a simpler approach. Users can sell items, search for listings, participate in auctions, and rate and comment on items. Administrative users have additional privileges, including auction management and viewing reports.

## Features

- User authentication system distinguishing Regular and Administrative Users
- New user registration with a simple form
- Capability for users to list items for auction, providing detailed information including item descriptions, categories, conditions, starting bids, and more
- Search functionality based on various criteria such as keywords, category, price range, and condition
- Auction system allowing for bidding, immediate purchase with a 'Get It Now' price option, and auction cancellation
- Ratings and comments system for user feedback on items
- Comprehensive reporting tools for administrative users to monitor and manage site activity

## User Interface

- The application can be implemented as a traditional standalone application or as a web application.
- Functional user interfaces without emphasis on aesthetic design.
- UI examples in the project description serve as a guide and may not capture all functionalities.

## Functionality Constraints

- Avoid additional functionalities not mentioned in the project specification.
- Do not create "catch-all" forms with unnecessary inputs.

## Auction Rules

- Items have a Starting Bid, a Minimum Sale Price (hidden from bidders), and optional Auction Length and Get It Now Price.
- Auction results are only finalized once the auction ends, with various conditions for determining the winner.

## User Experience

- Upon logging in, users are greeted with a main menu showing available actions.
- Administrative users see additional options related to site management and reports.
- Search results are presented in a list, with options to bid, view item details, or purchase immediately.
- Users can only rate items once and only on items they have won.

## Reporting System

- Administrative users have access to detailed reports like Category Report, User Report, Top Rated Items, Auction Statistics, and Cancelled Auction Details.
- The reporting system is designed to leverage SQL queries efficiently to retrieve and display relevant data.

## Development Notes

- Users need not worry about handling concurrent operations in the database.
- Ensure non-numeric data that appear as numbers are stored as strings.
- Normalized schemas are preferred, minimizing the use of NULL attributes.





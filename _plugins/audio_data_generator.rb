# Require ActiveSupport extensions for the String class
# This provides helpful string manipulation methods like `parameterize`.
require 'active_support/core_ext/string'

# Define a custom generator for Jekyll
module Jekyll
  # AudioDataGenerator is responsible for generating new audio entry pages
  class AudioDataGenerator < Generator
    # safe true means this generator will not modify site content or state in dangerous ways
    safe true

    # The generate method is called during Jekyll's build process
    def generate(site)
      # Load the 'audio_data' from the _data/audio_data.yml file
      audio_data = site.data['audio_data']['users']

      # Iterate over each user in the audio data
      audio_data.each do |user, entries|
        # Iterate over each audio entry for this user
        entries.each do |entry|
          # For each audio entry, create a new AudioEntryPage
          # This page will be created for the user and entry by calling the AudioEntryPage class
          site.pages << AudioEntryPage.new(site, site.source, user, entry)
        end
      end
    end
  end

  # Define a class for representing an individual audio entry page
  class AudioEntryPage < Page
    # Initialize the AudioEntryPage with the site, base, user, and entry data
    def initialize(site, base, user, entry)
      @site = site 
      @base = base 

      # Set the directory path for this audio entry page, e.g., /u/username
      @dir = File.join('u', user) # makes /u/username/entry-title.html

      # Set the page name based on the audio entry title, parameterized to be URL-safe
      @name = "#{entry['title'].parameterize}.html"  # Makes a filename like 'my-cool-audio.html'

      # Process the page (set up the page with the correct name)
      self.process(@name)

      # Read the layout template for this page from _layouts/entry.html
      self.read_yaml(File.join(base, '_layouts'), 'entry.html')

      # Set page-specific data, which can be used in the layout to render the page
      self.data['title'] = entry['title']      # Set the title of the audio entry
      self.data['description'] = entry['description']  # Set the description of the audio entry
      self.data['audio'] = entry['audio']      # Set the path to the audio file
      self.data['user'] = user                 # Set the username associated with the entry
    end
  end
end
